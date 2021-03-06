import pytest


def test_default_tag_exists_and_has_name(hlwm):
    assert hlwm.get_attr('tags.count') == '1'
    assert hlwm.get_attr('tags.0.name') == 'default'


def test_add_tag(hlwm):
    focus_before = hlwm.get_attr('tags.focus.name')

    hlwm.call('add foobar')

    assert hlwm.get_attr('tags.count') == '2'
    assert hlwm.get_attr('tags.1.client_count') == '0'
    assert hlwm.get_attr('tags.1.client_count') == '0'
    assert hlwm.get_attr('tags.1.curframe_wcount') == '0'
    assert hlwm.get_attr('tags.1.curframe_windex') == '0'
    assert hlwm.get_attr('tags.1.frame_count') == '1'
    assert hlwm.get_attr('tags.1.index') == '1'
    assert hlwm.get_attr('tags.1.name') == 'foobar'
    assert hlwm.get_attr('tags.focus.name') == focus_before


def test_use_tag(hlwm):
    assert hlwm.get_attr('tags.focus.index') == '0'
    hlwm.call('add foobar')

    hlwm.call('use foobar')

    assert hlwm.get_attr('tags.focus.index') == '1'
    assert hlwm.get_attr('tags.focus.name') == 'foobar'


def test_use_previous(hlwm):
    hlwm.call('add foobar')
    hlwm.call('use foobar')
    assert hlwm.get_attr('tags.focus.index') == '1'

    hlwm.call('use_previous')

    assert hlwm.get_attr('tags.focus.index') == '0'

    hlwm.call('use_previous')

    assert hlwm.get_attr('tags.focus.index') == '1'


@pytest.mark.parametrize("running_clients_num", [0, 1, 5])
def test_new_clients_increase_client_count(hlwm, running_clients, running_clients_num):
    assert hlwm.get_attr('tags.0.client_count') == str(running_clients_num)


def test_move_focused_client_to_new_tag(hlwm):
    hlwm.call('add foobar')
    assert hlwm.get_attr('tags.0.client_count') == '0'
    assert hlwm.get_attr('tags.1.client_count') == '0'

    winid, _ = hlwm.create_client()
    assert hlwm.get_attr('tags.0.client_count') == '1'
    assert hlwm.get_attr('tags.1.client_count') == '0'

    hlwm.call('move foobar')

    assert hlwm.get_attr('tags.0.client_count') == '0'
    assert hlwm.get_attr('tags.0.curframe_wcount') == '0'
    assert hlwm.get_attr('tags.1.client_count') == '1'
    assert hlwm.get_attr('tags.1.curframe_wcount') == '1'
    assert hlwm.get_attr('clients', winid, 'tag') == 'foobar'


def test_merge_tag_into_another_tag(hlwm):
    hlwm.call('add foobar')
    hlwm.create_client()
    hlwm.call('use_index 1')

    hlwm.call('merge_tag default foobar')

    assert hlwm.get_attr('tags.count') == '1'
    assert hlwm.get_attr('tags.0.index') == '0'
    assert hlwm.get_attr('tags.0.name') == 'foobar'


RENAMING_COMMANDS = [
    # commands for renaming the default tag
    ['set_attr', 'tags.by-name.default.name'],
    ['rename', 'default']]


@pytest.mark.parametrize("rename_command", RENAMING_COMMANDS)
def test_rename_tag(hlwm, hc_idle, rename_command):
    hlwm.call(rename_command + ['foobar'])

    assert hlwm.get_attr('tags.0.name') == 'foobar'
    assert hc_idle.hooks() == [['tag_renamed', 'foobar']]


@pytest.mark.parametrize("rename_command", RENAMING_COMMANDS)
def test_rename_tag_empty(hlwm, rename_command):
    hlwm.call_xfail(rename_command + [""]) \
        .expect_stderr('An empty tag name is not permitted')


@pytest.mark.parametrize("rename_command", RENAMING_COMMANDS)
def test_rename_tag_existing_tag(hlwm, rename_command):
    hlwm.call('add foobar')

    hlwm.call_xfail(rename_command + ["foobar"]) \
        .expect_stderr('"foobar" already exists')


def test_floating_invalid_parameter(hlwm):
    # passing a non-boolean must be handled
    hlwm.call_xfail('floating invalidvalue') \
        .expect_stderr('invalid argument')


@pytest.mark.parametrize("tiled_num", [3])
@pytest.mark.parametrize("floated_num", [2])
def test_client_count_attribute(hlwm, tiled_num, floated_num):
    hlwm.create_clients(tiled_num)
    floated = hlwm.create_clients(floated_num)
    for winid in floated:
        hlwm.call(f'attr clients.{winid}.floating true')

    assert int(hlwm.get_attr('tags.focus.client_count')) \
        == tiled_num + floated_num


@pytest.mark.parametrize("command", [
    "close_or_remove",
    "close_and_remove",
])
def test_close_and_or_remove_floating(hlwm, command):
    # set up some empty frames and a floating client
    hlwm.call('split explode')
    winid, proc = hlwm.create_client()
    hlwm.call(f'set_attr clients.{winid}.floating true')
    hlwm.call(f'jumpto {winid}')
    assert hlwm.get_attr('clients.focus.winid') == winid
    assert int(hlwm.get_attr('tags.focus.frame_count')) == 2

    # run close_or_remove / close_and_remove
    hlwm.call(command)

    # in any case no frame may have been removed
    assert int(hlwm.get_attr('tags.focus.frame_count')) == 2
    # and the client is closed:
    proc.wait(10)


def test_close_and_remove_with_one_client(hlwm):
    hlwm.call('split explode')
    winid, proc = hlwm.create_client()
    assert hlwm.get_attr('clients.focus.winid') == winid
    assert int(hlwm.get_attr('tags.focus.frame_count')) == 2

    hlwm.call('close_and_remove')

    # this closes the client and removes the frame
    assert int(hlwm.get_attr('tags.focus.frame_count')) == 1
    proc.wait(10)


def test_close_and_remove_with_two_clients(hlwm):
    hlwm.call('split explode')
    winid, proc = hlwm.create_client()
    other_winid, _ = hlwm.create_client()
    assert hlwm.get_attr('clients.focus.winid') == winid
    assert int(hlwm.get_attr('tags.focus.frame_count')) == 2

    hlwm.call('close_and_remove')

    # this closes the client, but does not remove the frame
    # since there is a client left
    assert int(hlwm.get_attr('tags.focus.frame_count')) == 2
    proc.wait(10)


def test_close_and_remove_without_clients(hlwm):
    hlwm.call('split explode')
    assert int(hlwm.get_attr('tags.focus.frame_count')) == 2

    hlwm.call('close_and_remove')

    # this acts like remove:
    assert int(hlwm.get_attr('tags.focus.frame_count')) == 1


def test_close_or_remove_client(hlwm):
    # This is like close_and_remove, but requires hitting
    # 'close_or_remove' twice.
    hlwm.call('split explode')
    winid, proc = hlwm.create_client()
    assert int(hlwm.get_attr('tags.focus.frame_count')) == 2

    # On the first invocation:
    hlwm.call('close_or_remove')
    # only close the client
    proc.wait(10)
    assert int(hlwm.get_attr('tags.focus.frame_count')) == 2

    # On the second invocation:
    hlwm.call('close_or_remove')
    # remove the frame
    assert int(hlwm.get_attr('tags.focus.frame_count')) == 1
