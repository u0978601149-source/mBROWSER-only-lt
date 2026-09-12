import sys
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import (QApplication, QMainWindow, QToolBar, QLineEdit,
                             QTabWidget)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage

class DevToolsWindow(QMainWindow):
    def __init__(self, page, parent=None):
        super().__init__(parent)
        self.setWindowTitle("mBROWSER - Kūrėjo įrankiai (DevTools)")
        self.resize(950, 650)
        self.view = QWebEngineView(self)
        self.setCentralWidget(self.view)
        page.setDevToolsPage(self.view.page())

class MBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("mBROWSER - MicroLox")
        self.setGeometry(100, 100, 1280, 800)

        # Saugumo nustatymai
        profile = QWebEngineProfile.defaultProfile()
        profile.setHttpUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies)

        # Skirtukų valdiklis
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.setCentralWidget(self.tabs)

        # Navigacijos juosta
        navbar = QToolBar("Navigacija")
        navbar.setMovable(False)
        self.addToolBar(navbar)

        back_btn = QAction("◀", self)
        back_btn.triggered.connect(self.current_back)
        navbar.addAction(back_btn)

        forward_btn = QAction("▶", self)
        forward_btn.triggered.connect(self.current_forward)
        navbar.addAction(forward_btn)

        reload_btn = QAction("⟳", self)
        reload_btn.triggered.connect(self.current_reload)
        navbar.addAction(reload_btn)

        new_tab_btn = QAction("＋ Naujas skirtukas", self)
        new_tab_btn.triggered.connect(lambda: self.add_new_tab("https://search.brave.com/", "MicroLox"))
        navbar.addAction(new_tab_btn)

        # Pilno ekrano mygtukas
        fullscreen_btn = QAction("⛶", self)
        fullscreen_btn.setToolTip("Pilnas ekranas (F11)")
        fullscreen_btn.triggered.connect(self.toggle_fullscreen)
        navbar.addAction(fullscreen_btn)

        # DevTools mygtukas
        devtools_btn = QAction("🛠️", self)
        devtools_btn.setToolTip("Kūrėjo įrankiai - DevTools (F12)")
        devtools_btn.triggered.connect(self.open_devtools)
        navbar.addAction(devtools_btn)

        navbar.addSeparator()

        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Įveskite URL arba ieškokite...")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        navbar.addWidget(self.url_bar)

        # F11 spartusis klavišas (pilnas ekranas)
        self.fullscreen_action = QAction(self)
        self.fullscreen_action.setShortcut(QKeySequence("F11"))
        self.fullscreen_action.triggered.connect(self.toggle_fullscreen)
        self.addAction(self.fullscreen_action)

        # F12 spartusis klavišas (DevTools)
        self.devtools_action = QAction(self)
        self.devtools_action.setShortcut(QKeySequence("F12"))
        self.devtools_action.triggered.connect(self.open_devtools)
        self.addAction(self.devtools_action)

        # Pradinis puslapis
        self.add_new_tab("https://search.brave.com/", "MicroLox Browser")

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def open_devtools(self):
        browser = self.tabs.currentWidget()
        if browser and isinstance(browser, QWebEngineView):
            # Sukuriame ir atidarome DevTools atskirame lange
            self.devtools_window = DevToolsWindow(browser.page(), self)
            self.devtools_window.show()

    def add_new_tab(self, url, label):
        browser = QWebEngineView()
        page = QWebEnginePage(QWebEngineProfile.defaultProfile(), browser)
        browser.setPage(page)
        
        page.setLifecycleState(QWebEnginePage.LifecycleState.Active)
        browser.setUrl(QUrl(url))
        
        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)

        browser.urlChanged.connect(lambda q, b=browser: self.update_url(q, b))
        browser.titleChanged.connect(lambda title, b=browser: self.update_title(title, b))

    def close_tab(self, i):
        if self.tabs.count() > 1:
            self.tabs.removeTab(i)

    def current_tab_changed(self, i):
        browser = self.tabs.currentWidget()
        if browser and isinstance(browser, QWebEngineView):
            if browser.page():
                browser.page().setLifecycleState(QWebEnginePage.LifecycleState.Active)
            self.url_bar.setText(browser.url().toString())

    def navigate_to_url(self):
        browser = self.tabs.currentWidget()
        if browser and isinstance(browser, QWebEngineView):
            url = self.url_bar.text()
            if not url.startswith("http"):
                url = "https://" + url
            browser.setUrl(QUrl(url))

    def update_url(self, q, browser):
        if self.tabs.currentWidget() == browser:
            self.url_bar.setText(q.toString())

    def update_title(self, title, browser):
        i = self.tabs.indexOf(browser)
        if i != -1:
            self.tabs.setTabText(i, title[:20] + "..." if len(title) > 20 else title)

    def current_back(self):
        b = self.tabs.currentWidget()
        if b: b.back()

    def current_forward(self):
        b = self.tabs.currentWidget()
        if b: b.forward()

    def current_reload(self):
        b = self.tabs.currentWidget()
        if b: b.reload()

app = QApplication(sys.argv)
window = MBrowser()
window.show()
sys.exit(app.exec())
