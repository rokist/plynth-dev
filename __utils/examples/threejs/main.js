var electron = require("electron")
const { protocol } = require('electron')
var path = require("path")
var fs = require("fs")
protocol.registerSchemesAsPrivileged([
  { scheme: 'esm', privileges: { bypassCSP: true } }
])

function on_app_ready() {
    protocol.registerBufferProtocol("esm", async (req, cb) => {
        const relpath = req.url.replace("esm://", "")
        const filepath = path.resolve(__dirname, relpath)
        const data = await fs.promises.readFile(filepath)
        cb({ mineType: "text/javascript", data })
    })

    var browserWindow = new electron.BrowserWindow(
            {x:200, y:200, width:700, height:580, webPreferences: { nodeIntegration: true }}
        );

    var url_dict = {
        pathname:require("path").join(__dirname, "index.html"), protocol:"file:", slashesd:true
    }

    browserWindow.loadURL(require("url").format(url_dict))
}

electron.app.on("ready", on_app_ready)
