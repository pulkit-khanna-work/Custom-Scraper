import * as cmn from '../common.js';

const args = cmn.getArgs();
const width = parseInt(args[0])
const height = parseInt(args[1])

await cmn.run({ runFunction: cmn.setViewPort, args: { width: width, height: height } })
