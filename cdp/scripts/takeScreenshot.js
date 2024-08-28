import * as fs from 'fs';

import * as cmn from '../common.js';

const args = cmn.getArgs();
const fileName = args[0];
const width = isNaN(args[1]) ? null : parseInt(args[1])
const height = isNaN(args[2]) ? null : parseInt(args[2])


async function takeScreenshot({ Page, Emulation, fileName, width = null, height = null }) {
  await cmn.setViewPort({ Emulation: Emulation, width: width, height: height });
  await cmn.sleep(5)


  const { data } = await Page.captureScreenshot({ format: 'jpeg', quality: 100, fromsurface: true, captureBeyondViewport: false });
  fs.writeFileSync(fileName, Buffer.from(data, 'base64'));

  cmn.print({ result: `Screenshot taken ${fileName}` })
  await cmn.setViewPort({ Emulation: Emulation });
}

await cmn.run({ runFunction: takeScreenshot, args: { fileName: fileName, width: width, height: height } })
