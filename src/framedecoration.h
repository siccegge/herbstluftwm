#ifndef __HLWM_FRAME_DECORATION_H_
#define __HLWM_FRAME_DECORATION_H_

#include "x11-types.h"

class HSTag;
class HSSlice;
class FrameDecoration;

class FrameDecorationData {
public:
    FrameDecorationData();
    bool visible;
    bool hasClients; // whether this frame holds clients at the moment
    bool hasParent;
    Rectangle geometry;
};

class FrameDecoration {
public:
    FrameDecoration(HSTag* tag);
    ~FrameDecoration();
    void render(const FrameDecorationData& data, bool isFocused);
    void updateVisibility(const FrameDecorationData& data, bool isFocused);
    void hide();

private:
    Window window;
    bool visible; // whether the window is visible at the moment
    bool window_transparent; // whether the window has a mask at the moment
    HSSlice* slice;
    HSTag* tag;
};

#endif
