from __future__ import annotations

from typing import Optional, Tuple

import mss
import numpy as np
import win32gui


def find_window(title_fragment: str) -> Optional[int]:
    target = title_fragment.lower().strip()
    found = []

    def cb(hwnd, _):
        if (
            win32gui.IsWindowVisible(hwnd)
            and target in win32gui.GetWindowText(hwnd).lower()
        ):
            found.append(hwnd)
        return True

    win32gui.EnumWindows(cb, None)

    if not found:
        return None

    found.sort(
        key=lambda h: (
            (win32gui.GetWindowRect(h)[2] - win32gui.GetWindowRect(h)[0])
            * (win32gui.GetWindowRect(h)[3] - win32gui.GetWindowRect(h)[1])
        ),
        reverse=True,
    )

    return found[0]


class WindowCapture:
    def __init__(self):
        self.sct = mss.mss()

    def get_window_rect(
        self,
        hwnd: int,
    ) -> Tuple[int, int, int, int]:
        return win32gui.GetWindowRect(hwnd)

    def capture(
        self,
        hwnd: int,
    ):
        left, top, right, bottom = self.get_window_rect(hwnd)

        width = max(1, right - left)
        height = max(1, bottom - top)

        shot = self.sct.grab(
            {
                "left": left,
                "top": top,
                "width": width,
                "height": height,
            }
        )

        # mss returns BGRA on Windows. Convert to BGR for OpenCV.
        frame = np.asarray(shot)[:, :, :3][:, :, ::-1].copy()

        return frame, (
            left,
            top,
            right,
            bottom,
        )

    # Compatibility method used by MainWindow.
    def capture_window(
        self,
        hwnd: int,
    ):
        return self.capture(hwnd)
