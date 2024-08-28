import CDP from 'chrome-remote-interface';

function print(message) {
  console.log(JSON.stringify(message))
}

async function sleep(time) {
  await new Promise(r => setTimeout(r, time * 1000))
}

function exit(code = 0) {
  process.exit(code)
}

function getArgs() {
  let args = [];
  for (const arg of JSON.parse(process.argv.slice(3))) {
    args.push(String(arg))
  }

  return args;
}

async function getClient() {
  const port = parseInt(process.argv[2]);
  const client = await CDP({ port: port });
  return client;
}

async function run({ runFunction, args = {} }) {
  const client = await getClient();
  const { Page, DOM, Runtime, Emulation, Input } = client;

  await Page.enable();
  await Runtime.enable();
  await DOM.enable();

  const { root } = await DOM.getDocument();
  const output = await runFunction({ client: client, Page: Page, Runtime: Runtime, DOM: DOM, Emulation: Emulation, Input: Input, root: root, ...args });

  await client.close();

  if (output) {
    return output;
  }
}


async function getNodeIds({ DOM, nodeId, selector }) {
  const { nodeIds } = await DOM.querySelectorAll({ nodeId: nodeId, selector: selector });
  return nodeIds;
}

async function getNodeId({ DOM, nodeId, selector, targetNodeId = -1 }) {
  const nodeIds = await getNodeIds({ DOM: DOM, nodeId: nodeId, selector: selector });
  if (targetNodeId == -1) {
    return nodeIds[0];
  } else {
    return nodeIds[nodeIds.indexOf(targetNodeId)];
  }
}

async function setViewPort({ Emulation, width = 1920, height = 1080 }) {
  const deviceMetrics = {
    width: width,
    height: height,
    deviceScaleFactor: 1,
    mobile: false,
    fitWindow: false,
  };
  await Emulation.setDeviceMetricsOverride(deviceMetrics);
  await Emulation.setVisibleSize({ width: width, height: height });
}

async function scrollIntoView({ DOM, nodeId }) {
  await DOM.scrollIntoViewIfNeeded({ nodeId: nodeId })
}

export { print, sleep, exit, run, getClient, getArgs, getNodeIds, getNodeId, setViewPort, scrollIntoView }
