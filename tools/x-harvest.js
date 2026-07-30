/*
 * x-harvest.js — pull a public X timeline into a JSON file, using your own
 * already-logged-in browser session.
 *
 * WHAT IT DOES: reads posts out of the page as it auto-scrolls, dedupes them by
 * status ID, and downloads the result as JSON.
 *
 * WHAT IT DOES NOT DO: it never reads your cookies, tokens, password, DMs, or
 * account settings, and it makes no network requests of its own. The only
 * outbound action is a local file download. Read it before you run it.
 *
 * HOW TO RUN
 *   1. Open the timeline you want (see RECOMMENDED PAGES below).
 *   2. F12 -> Console tab. X prints a big red self-XSS warning; if it asks you
 *      to type something before pasting, do that.
 *   3. Paste this whole file, press Enter, and leave the tab in the foreground
 *      and untouched. Background tabs get throttled and scrolling stalls.
 *   4. When it finishes it downloads x-<name>-<n>posts.json.
 *
 * RECOMMENDED PAGES
 *   Profile "Posts" tab   -> his own posts
 *   Profile "Replies" tab -> exits are often posted as replies. Run it here too.
 *   Better, for full coverage, use search in dated slices so nothing is dropped:
 *     https://x.com/search?q=from%3AStockspy1%20since%3A2024-01-01%20until%3A2024-07-01&f=live
 *   Walk the window forward six months at a time and run the script on each.
 *   Overlapping windows are fine; duplicates are removed at merge time.
 */
(async () => {
  const KEEP_AUTHOR = 'Stockspy1'; // only keep posts by this handle; '' keeps everyone
  const STOP_BEFORE = '2000-01-01'; // stop once posts get older than this date
  const IDLE_LIMIT = 20; // stop after this many scrolls that surface nothing new
  const SCROLL_PAUSE = 800; // ms between scrolls; raise if posts load slowly

  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const posts = new Map();
  let oldest = null;

  const harvest = () => {
    for (const article of document.querySelectorAll('article[data-testid="tweet"]')) {
      const time = article.querySelector('time[datetime]');
      const link = time && time.closest('a[href*="/status/"]');
      if (!link) continue;

      const match = link.getAttribute('href').match(/^\/([^/]+)\/status\/(\d+)/);
      if (!match) continue;

      const [, author, id] = match;
      if (posts.has(id)) continue;

      const date = time.getAttribute('datetime');
      if (!oldest || date < oldest) oldest = date;
      if (KEEP_AUTHOR && author.toLowerCase() !== KEEP_AUTHOR.toLowerCase()) continue;

      const body = article.querySelector('div[data-testid="tweetText"]');
      posts.set(id, {
        id,
        author,
        date,
        text: body ? body.innerText : '',
        isRepost: !!article.querySelector('[data-testid="socialContext"]'),
        url: `https://x.com/${author}/status/${id}`,
      });
    }
  };

  let idle = 0;
  while (idle < IDLE_LIMIT) {
    const before = posts.size;
    harvest();
    idle = posts.size > before ? 0 : idle + 1;

    if (oldest && oldest < STOP_BEFORE) {
      console.log(`Reached ${oldest}, which is past the ${STOP_BEFORE} cutoff. Stopping.`);
      break;
    }

    console.log(`${posts.size} posts kept | oldest ${oldest || 'n/a'} | idle ${idle}/${IDLE_LIMIT}`);
    window.scrollBy(0, window.innerHeight * 0.85);
    await sleep(SCROLL_PAUSE);
  }

  harvest();

  const rows = [...posts.values()].sort((a, b) => a.date.localeCompare(b.date));
  if (!rows.length) {
    console.warn('Nothing captured. Check that KEEP_AUTHOR matches the handle on this page.');
    return;
  }

  const name = `x-${KEEP_AUTHOR || 'all'}-${rows.length}posts.json`;
  const url = URL.createObjectURL(
    new Blob([JSON.stringify(rows, null, 2)], { type: 'application/json' })
  );
  Object.assign(document.createElement('a'), { href: url, download: name }).click();
  URL.revokeObjectURL(url);

  console.log(`Done. ${rows.length} posts, ${rows[0].date} through ${rows[rows.length - 1].date}.`);
  console.log(`Saved as ${name}`);
})();
