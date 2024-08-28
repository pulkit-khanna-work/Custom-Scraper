import * as cmn from '../common.js';

async function getRootId({ root }) {
  return root.nodeId;
}

const rootId = await cmn.run({ runFunction: getRootId })
cmn.print({ "rootId": rootId });
