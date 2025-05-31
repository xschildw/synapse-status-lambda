const STATUSPAGE_API_URL = "https://api.statuspage.io/v1/pages";

export const handler = async () => {
  try {
    const repoStatus = await getStatus(process.env.REPO_STATUS_ENDPOINT);
    const websiteStatus = await getStatus(process.env.WEBSITE_URL_ENDPOINT);

    await updateComponentStatus(
      process.env.STATUS_PAGE_IO_REPO_COMPONENT_ID,
      repoStatus.status === "READ_WRITE" ? "operational" : "under_maintenance",
      repoStatus.currentMessage
    );

    await updateComponentStatus(
      process.env.STATUS_PAGE_IO_WEBSITE_COMPONENT_ID,
      websiteStatus.statusCode === 200 ? "operational" : "major_outage",
      websiteStatus.statusMessage
    );

    console.log("Status update completed.", );
  } catch (err) {
    console.error("Error in handler:", err);
    throw err;
  }
};

async function getStatus(endpoint) {
  const res = await fetch(endpoint, { headers: { "User-Agent": "statuspage-lambda" } });
  const text = await res.text();

  try {
    const json = JSON.parse(text);
    return { status: json.status, currentMessage: json.currentMessage, statusCode: res.status };
  } catch {
    return { statusCode: res.status, statusMessage: text };
  }
}

async function updateComponentStatus(componentId, status, message) {
  const pageId = process.env.STATUS_PAGE_IO_PAGE_ID;
  const apiKey = process.env.STATUS_PAGE_IO_API_KEY;

  const res = await fetch(`${STATUSPAGE_API_URL}/${pageId}/components/${componentId}.json`, {
    method: "PATCH",
    headers: {
      Authorization: `OAuth ${apiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ component: { status } }),
  });

  if (!res.ok) {
    const body = await res.text();
    console.error(`Failed to update component ${componentId}:`, body);
    throw new Error(`StatusPage update failed for component ${componentId}`);
  }

  console.log(`Updated component ${componentId} to status: ${status}`);
  if (message) console.log(`Message: ${message}`);
}
