import * as cmn from '../common.js';

const args = cmn.getArgs();
const expression = args[0];

async function executeScript({ Runtime, expression }) {
  const { result } = await Runtime.evaluate({ expression: expression });
  return result;
}

const result = await cmn.run({ runFunction: executeScript, args: { expression: expression } })

if (result.subtype == "error" || result.type == 'undefined') {
  cmn.print({ "value": null })
} else {
  cmn.print({ "value": result.value })
}

