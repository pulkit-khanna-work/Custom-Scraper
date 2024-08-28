import * as cmn from '../common.js';

const url = cmn.getArgs()[0];

async function navigate({ Page, url }) {
  await Page.enable();
  await Page.navigate({ url: url });
  await Page.loadEventFired();
}

await cmn.run({ runFunction: navigate, args: { url: url } })
