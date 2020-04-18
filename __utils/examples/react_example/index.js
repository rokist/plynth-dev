var electron = require("electron")

function on_app_ready() {
    let browserWindow = new electron.BrowserWindow(
            {x:200, y:200, width:600, height:480}
    );

    let url_dict = {
        pathname:require("path").join(__dirname, "index.html"), protocol:"file:", slashesd:true
    }

    browserWindow.loadURL(require("url").format(url_dict))
}

electron.app.on("ready", on_app_ready)


