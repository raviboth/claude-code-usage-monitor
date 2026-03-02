from collections.abc import Callable
from io import BytesIO

from PIL import Image as PILImage
from PyQt6.QtGui import QIcon, QImage, QPixmap
from PyQt6.QtWidgets import QMenu, QSystemTrayIcon

from src.api import UsageData
from src.icons import render_tray_icon
from src.utils import format_reset_time, format_utilization


def _pil_to_qicon(pil_image: PILImage.Image) -> QIcon:
    """Convert a PIL Image to a QIcon with Retina support."""
    buf = BytesIO()
    pil_image.save(buf, format="PNG")
    buf.seek(0)
    qimage = QImage.fromData(buf.read())
    # Set device pixel ratio for Retina (image is 44px, display at 22pt)
    qimage.setDevicePixelRatio(2.0)
    pixmap = QPixmap.fromImage(qimage)
    return QIcon(pixmap)


class TrayManager:
    def __init__(
        self,
        on_open_dashboard: Callable[[], None],
        on_refresh: Callable[[], None],
        on_quit: Callable[[], None],
    ) -> None:
        self._on_open_dashboard = on_open_dashboard
        self._on_refresh = on_refresh
        self._on_quit = on_quit
        self._last_data: UsageData | None = None
        self._error: str | None = None
        self._stale = False

        icon_image = render_tray_icon(None)
        self._tray = QSystemTrayIcon(_pil_to_qicon(icon_image))
        self._tray.setToolTip("Claude Code Usage Monitor")

        self._menu = QMenu()
        self._build_menu()
        self._tray.setContextMenu(self._menu)

    def _build_menu(self) -> None:
        self._menu.clear()

        if self._error and self._last_data is None:
            action = self._menu.addAction(self._error)
            action.setEnabled(False)
        elif self._last_data:
            stale_suffix = " (stale)" if self._stale else ""
            d = self._last_data

            five_h = f"5h: {format_utilization(d.five_hour.utilization)} \u00b7 {format_reset_time(d.five_hour.resets_at)}{stale_suffix}"
            action = self._menu.addAction(five_h)
            action.setEnabled(False)

            seven_d = f"7d: {format_utilization(d.seven_day.utilization)} \u00b7 {format_reset_time(d.seven_day.resets_at)}{stale_suffix}"
            action = self._menu.addAction(seven_d)
            action.setEnabled(False)

            if d.seven_day_opus:
                opus = f"Opus 7d: {format_utilization(d.seven_day_opus.utilization)} \u00b7 {format_reset_time(d.seven_day_opus.resets_at)}{stale_suffix}"
                action = self._menu.addAction(opus)
                action.setEnabled(False)

            if d.extra_usage and d.extra_usage.is_enabled:
                extra = f"Extra: ${d.extra_usage.used_credits:.2f}/${d.extra_usage.monthly_limit:.2f} ({format_utilization(d.extra_usage.utilization)}){stale_suffix}"
                action = self._menu.addAction(extra)
                action.setEnabled(False)
        else:
            action = self._menu.addAction("Loading...")
            action.setEnabled(False)

        self._menu.addSeparator()
        self._menu.addAction("Open Dashboard", self._on_open_dashboard)
        self._menu.addAction("Refresh Now", self._on_refresh)
        self._menu.addSeparator()
        self._menu.addAction("Quit", self._on_quit)

    def update(self, data: UsageData | None, error: str | None) -> None:
        if data:
            self._last_data = data
            self._stale = False
            self._error = None
            util = data.five_hour.utilization
        elif error:
            self._stale = self._last_data is not None
            self._error = error
            util = self._last_data.five_hour.utilization if self._last_data else None
        else:
            util = None

        self._tray.setIcon(_pil_to_qicon(render_tray_icon(util)))
        self._build_menu()

    def show(self) -> None:
        """Show the tray icon."""
        self._tray.show()

    def hide(self) -> None:
        """Hide the tray icon."""
        self._tray.hide()
