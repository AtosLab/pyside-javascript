import sys
from os.path import dirname, join
 
#from PySide.QtCore import QApplication
from PySide.QtCore import QObject, Slot, Signal
from PySide.QtGui import QApplication, QFileDialog
from PySide.QtWebKit import QWebView, QWebSettings
from PySide.QtNetwork import QNetworkRequest
 
 
web     = None
myPage  = None
myFrame = None
 
class HubOpenFile(QObject):
 
    def __init__(self):
        super(HubOpenFile, self).__init__()
 
 
    @Slot(str)
    def connect(self, config):

        txtFileName = QFileDialog.getOpenFileNames(None, "Open")[0]
        txtFileName = str(txtFileName).replace("[u'",'').replace("']",'')
        print (txtFileName)

        text = open(txtFileName).read()
        self.on_file_open_event.emit(text)
 
    @Slot(str)
    def disconnect(self, config):
        print (config)
 
    on_file_open_event = Signal(str)
    on_connect = Signal(str)
    on_disconnect = Signal(str)

class HubSaveFile(QObject):
 
    def __init__(self):
        super(HubSaveFile, self).__init__()
 
 
    @Slot(str)
    def connect(self, config):
        txtFileName = QFileDialog.getSaveFileName(None, "Save")
        print (txtFileName)
        txtFileName = str(txtFileName).replace("(u'",'').replace("', u'')",'')
        print (txtFileName)

        file = open(txtFileName,'w') 
 
        file.write(config)
         
        file.close() 
        self.on_file_save_event.emit("Success")
 
    @Slot(str)
    def disconnect(self, config):
        print (config)
 
    on_file_save_event = Signal(str)
    on_connect = Signal(str)
    on_disconnect = Signal(str)
 
myHubOpenFile = HubOpenFile()
myHubSaveFile = HubSaveFile()
 
class HTMLApplication(object):
 
    def show(self):
        #It is IMPERATIVE that all forward slashes are scrubbed out, otherwise QTWebKit seems to be
        # easily confused
        kickOffHTML = join(dirname(__file__).replace('\\', '/'), "www/index.html").replace('\\', '/')
 
        #This is basically a browser instance
        self.web = QWebView()
 
        #Unlikely to matter but prefer to be waiting for callback then try to catch
        # it in time.
        self.web.loadFinished.connect(self.onLoad)
        self.web.load(kickOffHTML)
 
        self.web.show()
 
    def onLoad(self):
        if getattr(self, "myHubOpenFile", False) == False:
            self.myHubOpenFile = HubOpenFile()

        if getattr(self, "myHubSaveFile", False) == False:
            self.myHubSaveFile = HubSaveFile()
 
        #This is the body of a web browser tab
        self.myPage = self.web.page()
        self.myPage.settings().setAttribute(QWebSettings.DeveloperExtrasEnabled, True)
        #This is the actual context/frame a webpage is running in.  
        # Other frames could include iframes or such.
        self.myFrame = self.myPage.mainFrame()
        # ATTENTION here's the magic that sets a bridge between Python to HTML
        self.myFrame.addToJavaScriptWindowObject("my_HubOpenFile", myHubOpenFile)
        self.myFrame.addToJavaScriptWindowObject("my_HubSaveFile", myHubSaveFile)
 
        #Tell the HTML side, we are open for business
        self.myFrame.evaluateJavaScript("ApplicationIsReady()")
 
 
#Kickoff the QT environment
app = QApplication(sys.argv)
 
myWebApp = HTMLApplication()
myWebApp.show()
 
sys.exit(app.exec_())