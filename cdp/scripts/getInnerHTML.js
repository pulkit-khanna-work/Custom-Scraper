import * as cmn from '../common.js';

async function getObjectId(DOM, nodeId) {
  const { object: { objectId } } = await DOM.resolveNode({ nodeId: nodeId })
  return objectId;
}

async function getProperties(Runtime, objectId) {
  const { result: properties } = await Runtime.getProperties({ objectId: objectId })
  return properties;
}

async function getInnerHTML({ DOM, Runtime, root, selector, targetNodeId }) {
  const nodeId = await cmn.getNodeId({ DOM: DOM, nodeId: root.nodeId, selector: selector, targetNodeId: targetNodeId });
  const objectId = await getObjectId(DOM, nodeId);
  const properties = await getProperties(Runtime, objectId);

  let text = "";
  for (const property of properties) {
    if (property.name == "innerHTML") {
      text = property.value.value.trim();
      break;
    }
  }

  return text;
}

const args = cmn.getArgs()
const selector = args[0];
const targetNodeId = parseInt(args[1]);

const text = await cmn.run({ runFunction: getInnerHTML, args: { selector: selector, targetNodeId: targetNodeId } })
cmn.print({ 'text': text })
