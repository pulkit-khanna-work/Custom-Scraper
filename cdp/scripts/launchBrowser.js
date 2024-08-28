import * as ChromeLauncher from 'chrome-launcher';
import * as cmn from '../common.js';


const chrome = await ChromeLauncher.launch({ ignoreDefaultFlags: true, chromeFlags: ['--start-maximized', '--start-fullscreen', '--disable-notifications', '--no-first-run', '--no-default-browser-check'] });
cmn.print({ "port": chrome.port, "pid": chrome.pid })
// cmn.exit()
