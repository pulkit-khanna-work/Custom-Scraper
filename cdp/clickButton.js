import * as cmn from '../common.js';

async function buttonClick({ Input, x, y }) {
  const options = {
    x: x,
    y: y,
    button: 'left',
    clickCount: 1
  };
  await Promise.resolve().then(() => {
    options.type = 'mousePressed';
    return Input.dispatchMouseEvent(options);
  }).then(async () => {
    await cmn.sleep(1)
    options.type = 'mouseReleased';
    return Input.dispatchMouseEvent(options);
  }).catch((err) => {
    throw err
  })
}

const args = cmn.getArgs()
const x = parseInt(args[0])
const y = parseInt(args[1])

await cmn.run({ runFunction: buttonClick, args: { x: x, y: y } })
