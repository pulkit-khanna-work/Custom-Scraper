import * as cmn from '../common.js';

const args = cmn.getArgs();
const selector = args[0];

// const nodeId = await cmn.get
async function getNodeIds({ DOM, root, selector }) {
  return await cmn.getNodeIds({ DOM: DOM, nodeId: root.nodeId, selector: selector });
}

const nodeIds = await cmn.run({ runFunction: getNodeIds, args: { selector: selector } })

cmn.print({ nodeIds: nodeIds })
