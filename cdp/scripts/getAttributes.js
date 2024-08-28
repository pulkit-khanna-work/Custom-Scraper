import * as cmn from '../common.js';

const args = cmn.getArgs();
const selector = args[0];
const targetNodeId = parseInt(args[1]);

async function getAttributes({ DOM, root, selector, targetNodeId }) {
  const nodeId = await cmn.getNodeId({ DOM: DOM, nodeId: root.nodeId, selector: selector, targetNodeId: targetNodeId })
  const { attributes } = await DOM.getAttributes({ nodeId: nodeId });
  return attributes;
}

const attributes = await cmn.run({ runFunction: getAttributes, args: { selector: selector, targetNodeId: targetNodeId } });
cmn.print({ attributes: attributes })
