import * as cmn from '../common.js';

async function scrollIntoView({ DOM, root, selector, nodeId }) {
  const scrollIntoNodeId = cmn.getNodeId({ DOM: DOM, nodeId: root.nodeId, selector: selector, targetNodeId: nodeId })
  await cmn.scrollIntoView({ DOM: DOM, nodeId: scrollIntoNodeId })
}

const args = cmn.getArgs()
const selector = args[0]
const nodeId = parseInt(args[1])
await cmn.run({ runFunction: scrollIntoView, args: { selector: selector, nodeId: nodeId } })
