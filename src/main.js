const url = require('url');
const path = require('path');
const { app, BrowserWindow } = require('electron');
const electronReload = require('electron-reload')(__dirname, {
	electron: path.join(__dirname, 'node_modules', '.bin', 'electron')
});

function onReady() {
	win = new BrowserWindow({
		width: 900,
		height: 600,
		title: "QGUI",
		resizable: true,
		webPreferences: {
			contextIsolation: false,
			nodeIntegration: true
		}
	});
	win.loadURL(`http://localhost:4200`);
	win.setMenu(null);
	win.webContents.openDevTools({ mode: 'detach' });
}

app.on('ready', onReady);

