import * as cmn from '../common.js';

const args = cmn.getArgs();
const selector = args[0];
const targetNodeId = parseInt(args[1]);

async function getBoxModel({ DOM, root, selector, targetNodeId }) {
  const nodeId = await cmn.getNodeId({ DOM, nodeId: root.nodeId, selector: selector, targetNodeId: targetNodeId });
  await cmn.scrollIntoView({ DOM: DOM, nodeId: nodeId })
  const output = await DOM.getBoxModel({ nodeId: nodeId });
  return output;
}

const boxModel = await cmn.run({ runFunction: getBoxModel, args: { selector: selector, targetNodeId: targetNodeId } });
const coords = { x: Math.round(boxModel.model.content[0] + boxModel.model.width / 2), y: Math.round(boxModel.model.content[1] + boxModel.model.height / 2) };
cmn.print({ coords: coords })
