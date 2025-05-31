import { handler, getStatus, updateComponentStatus } from "../../lambda/statuspage_updater.mjs";

describe("getStatus", () => {
  beforeEach(() => {
    global.fetch = jest.fn();
  });

  test("parses JSON body", async () => {
    fetch.mockResolvedValue({
      status: 200,
      text: () =>
        Promise.resolve('{"status":"READ_WRITE","currentMessage":"All good"}'),
    });
    const out = await getStatus("any-url");
    expect(out).toEqual({
      status: "READ_WRITE",
      currentMessage: "All good",
      statusCode: 200,
    });
  });

  test("returns raw on parse error", async () => {
    fetch.mockResolvedValue({
      status: 503,
      text: () => Promise.resolve("<html>oops</html>"),
    });
    const out = await getStatus("any-url");
    expect(out).toEqual({
      statusCode: 503,
      statusMessage: "<html>oops</html>",
    });
  });
});

describe("updateComponentStatus", () => {
  beforeEach(() => {
    global.fetch = jest.fn();
    jest.spyOn(console, "error").mockImplementation(() => {});
    jest.spyOn(console, "log").mockImplementation(() => {});
    process.env.STATUS_PAGE_IO_API_KEY = "ABC";
    process.env.STATUS_PAGE_IO_PAGE_ID = "PAGE123";
  });

  test("succeeds on ok response", async () => {
    fetch.mockResolvedValue({ ok: true, status: 200 });
    await expect(
      updateComponentStatus("COMP1", "operational")
    ).resolves.toBeUndefined();
    expect(fetch).toHaveBeenCalledWith(
      "https://api.statuspage.io/v1/pages/PAGE123/components/COMP1.json",
      expect.objectContaining({
        method: "PATCH",
        headers: expect.objectContaining({
          Authorization: "OAuth ABC",
        }),
        body: JSON.stringify({ component: { status: "operational" } }),
      })
    );
  });

  test("throws on bad response", async () => {
    fetch.mockResolvedValue({
      ok: false,
      status: 400,
      text: () => Promise.resolve("bad"),
    });
    await expect(
      updateComponentStatus("COMP1", "down")
    ).rejects.toThrow("StatusPage update failed");
    expect(console.error).toHaveBeenCalledWith(
      expect.stringContaining("Failed to update component")
    );
  });
});

describe("handler orchestration", () => {
  beforeEach(() => {
    global.fetch = jest.fn();
    jest.spyOn(console, "error").mockImplementation(() => {});
    process.env.STATUS_PAGE_IO_REPO_COMPONENT_ID = "R1";
    process.env.STATUS_PAGE_IO_WEBSITE_COMPONENT_ID = "W1";
    process.env.STATUS_PAGE_IO_PAGE_ID = "PAGE123";
    process.env.STATUS_PAGE_IO_API_KEY = "ABC";
    process.env.REPO_STATUS_ENDPOINT = "repo-url";
    process.env.WEBSITE_URL_ENDPOINT = "web-url";
  });

  test("happy path", async () => {
    fetch
      .mockResolvedValueOnce({
        status: 200,
        text: () =>
          Promise.resolve('{"status":"READ_WRITE","currentMessage":"OK"}'),
      })
      .mockResolvedValueOnce({
        status: 200,
        text: () => Promise.resolve("hi"),
      })
      .mockResolvedValueOnce({ ok: true, status: 200 })
      .mockResolvedValueOnce({ ok: true, status: 200 });

    await expect(handler()).resolves.toBeUndefined();
    expect(fetch).toHaveBeenCalledTimes(4);
  });

  test("handler bubbles errors", async () => {
    fetch.mockRejectedValue(new Error("network"));
    await expect(handler()).rejects.toThrow("network");
    expect(console.error).toHaveBeenCalledWith(
      "Error in handler:",
      expect.any(Error)
    );
  });
});
