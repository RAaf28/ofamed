# ofamed.com Rebuild: End-to-End Plan (for Claude Code)

> Hand this file to Claude Code at the repo root. Work phase by phase. Do not skip gates. When something here says **ASK**, stop and ask the human instead of guessing.

---

## 0. How to work on this project

**Rules of engagement**
1. Work in the order of the phases in section 12. Finish a phase (all acceptance criteria met) before starting the next.
2. At the start of Phase 1, copy this file to `docs/PLAN.md` and create `PROGRESS.md` (template in section 16). After every task: update `PROGRESS.md`.
3. Per task loop: plan briefly → implement → run tests → verify visually with Playwright MCP (for UI work) → update `PROGRESS.md` → commit.
4. Commits: small, conventional (`feat:`, `fix:`, `chore:`, `docs:`, `test:`). Never commit `.env`, credentials, database dumps, or customer data.
5. **Never invent** product data, prices, certifications, registration numbers, statistics, testimonials, or legal text. Use clearly marked placeholders (`[Nama Produk]`, `[No. AKL/AKD]`) and list them in `docs/CONTENT-TODO.md`.
6. **Gates** (marked 🚧) require explicit human approval before continuing.
7. If reality contradicts this plan (hosting can't run the stack, a package is unavailable), stop, explain, and propose options. Do not silently change the architecture.
8. Language: code, comments, commits, docs in **English**. Public site copy and admin UI in **Indonesian (id-ID)**. Timezone `Asia/Jakarta`. Currency format IDR (`Rp1.250.000`).

---

## 1. Project context

**Client:** PT. Ofafa Duta Medika, a medical equipment and hospital supplier / distributor in Indonesia.
**Brands shown on the old site:** Ofafa Beauty Care, Ofahusada.
**Address (old site, confirm):** Ruko Rose Garden 8/18, Grand Galaxy City, Jaka Setia, Bekasi Selatan, Jawa Barat.
**Phone (old site, confirm):** +62 21 8275 5489.

**What happened**
- The original site was a one-page WordPress company profile (Hestia theme by ThemeIsle). The developer who built it left.
- The site now returns "connection timed out". Hostinger `public_html` is empty and there are no file or database backups, so there is nothing to restore.
- The old design and text survive in the Wayback Machine (`web.archive.org`, 23 captures, last one 2025-07-13). Images are mostly missing there.
- Old site had **no cart or payments**. "Online shop" was only links to Shopee and WhatsApp. No customer or order data was lost.

**Current infrastructure (verify in Phase 0, do not assume)**
- Domain `ofamed.com`: registered in the client's Hostinger account, active until 2028-05-11.
- Hosting: Hostinger "Single Web Hosting", about 10 GB disk and 1 GB RAM, server IP `153.92.11.164`. Plan was **expiring around 2026-10-15** unless renewed; owner was advised to renew 1 month first.
- Nameservers: `ns1.dns-parking.com`, `ns2.dns-parking.com`. The `www` record is a CNAME to Hostinger's CDN. Hostinger dashboard showed "domain is being connected" for weeks (stuck), and SSL was off. The A record for `@` has **not been checked yet**.

**Root cause to design against:** the site depended on one person. Everything must end up in the client's name, documented, and backed up.

---

## 2. Scope

**In scope (Package A: static site + simple product CRUD)**
- Redesigned company profile: Home, About, Contact. Responsive, SEO basics.
- Public catalog: product list, category filter, search, product detail page.
- Admin panel: login, product CRUD, category CRUD, brand CRUD, image upload, site settings, inquiry inbox.
- "Request a Quote" (WhatsApp prefilled message + inquiry form stored in DB and emailed to the admin).
- SSL, backups, handover docs, one-page admin guide.

**Out of scope (do not build; politely flag if asked)**
- Cart, checkout, online payment, customer accounts, shipping calculation, stock/ERP integration.
- Multi-language, blog, product reviews.
- Product photography and copywriting.

These may come later as "Phase 3: ordering" under a separate quote. Keep the data model extensible, but do not build for it now.

---

## 3. Architecture and tech decisions

**Chosen stack (subject to the Phase 0 gate)**
- **Laravel** (latest stable supported by the hosting's PHP version) + **Filament** admin panel (version compatible with that Laravel).
- **MySQL** (Hostinger-provided).
- **Blade + Tailwind CSS + Alpine.js** for the public site. Server-rendered for SEO. Catalog filters work via plain GET query params (progressive enhancement, no JS required).
- **Vite** build done **locally/in CI**, never on the server. Built assets (`public/build`) are included in the deploy.
- **Pest** for tests, **Laravel Pint** for style, **Larastan** (level 5+) if it adds no friction.
- **Playwright MCP** for visual verification and responsive checks.
- Images: upload originals, generate WebP thumbnails with GD or Imagick (verify support in Phase 0).
- Mail: SMTP (Hostinger mailbox) for inquiry notifications.
- Source control: GitHub repository **owned by the client** (or transferred to them at handover).

**Why this stack:** the existing hosting is shared PHP hosting, so Laravel + Filament runs there, gives a real admin panel for free, and leaves a clean upgrade path to payments later. Node-based stacks would need a VPS.

**Fallback if Phase 0 shows Laravel can't run on this hosting** (PHP too old, missing extensions, no way to deploy): **ASK** the owner. Options: (a) upgrade the hosting plan, (b) WordPress with a "Produk" custom post type and ACF/CPT UI, (c) VPS. Do not choose silently.

**Shared-hosting deployment constraints to plan for**
- Document root is `public_html`. Laravel's web root is `public/`. Use one of: app outside `public_html` with `public/` contents in `public_html` and adjusted paths in `index.php`, or point the domain/subdomain's document root to `public/` if the panel allows it. Pick in Phase 0 and document in `docs/DEPLOYMENT.md`.
- No Node on server → commit/ship built assets via CI artifact or local build.
- Cron via hPanel for the scheduler (`php artisan schedule:run` every minute) and queue (`queue:work --stop-when-empty` via schedule) if needed. Prefer `QUEUE_CONNECTION=sync` unless Phase 0 shows cron/queues are reliable.

---

## 4. Design

**Status:** the client is choosing between three homepage mockups (A, B, C). 🚧 **ASK which one was chosen** before Phase 2. Fill in: `CHOSEN_DESIGN = ___`.

Mockup canvas (owner access only): https://claude.ai/artifact/4yzxPGXEzn8gDQyuT4Sivy
Claude Code likely can't open it. **ASK the owner to export screenshots** of the chosen option into `design/reference/` (desktop and mobile). Keep this folder as the visual source of truth and do not overwrite it. Compare against it with Playwright after each UI task.

**Design tokens by option**

| | A: Klinis Bersih | B: Navy Korporat | C: Hangat Modern |
|---|---|---|---|
| Font(s) | Plus Jakarta Sans | DM Serif Display (headings) + DM Sans | Outfit |
| Primary | `#D7263D` red | `#0E1B2E` navy | `#C8372D` red |
| Accent | `#FDEDEE` soft red bg | `#5BD1C4` teal (on dark), `#1B8A7F` teal (on light) | `#4A6B55` sage, `#EADBC8` sand |
| Surface | `#FFFFFF`, `#F1F3F5` | `#F4F7FA`, footer `#0A1422` | `#FAF6F1` warm, cards `#FFFFFF` |
| Text | `#1A2433`, muted `#44505F` | `#0E1B2E`, muted `#44505F` | `#2B2420`, muted `#5E524A` |
| Shape | 8 px buttons, 14 px cards | 4 px buttons, sharp rows | pill buttons, 24–32 px cards |
| Catalog style | 3-column cards | table-like rows | rounded cards, bento tiles |

**Design rules**
- The mockups cover **the homepage only**. Catalog, product detail, About, Contact, 404, and mobile layouts must be designed by you in the same system. 🚧 Show screenshots to the owner before finishing Phase 2 and Phase 4.
- Mobile-first. Test 360, 390, 768, 1024, 1280, 1440 px wide.
- Contrast: text ≥ 4.5:1 (3:1 for 24 px+). Touch targets ≥ 44 px. Real `<button>`, `<a>`, `<label>`. No emoji as icons. Visible focus states.
- Avoid generic AI-looking layouts: no gradient washes, no identical card walls with no hierarchy. Use real content structure and spacing.
- Logos: ASK for the original logo files for PT. Ofafa Duta Medika, Ofafa Beauty Care, Ofahusada. Until then, use text wordmarks and note it in `CONTENT-TODO.md`.

---

## 5. Content

**Source copy from the old site (Wayback snapshot). Owner must approve; reword freely but keep the meaning.**

- Tagline: *Medical Equipment and Hospital Supplier*
- Headline: *Indonesia's Medical Equipment Distributor*
- Intro: "PT. Ofafa Duta Medika merupakan perusahaan distributor alat kesehatan di Indonesia yang memiliki visi dan misi yang berintegritas tinggi serta jangkauan global yang dipersembahkan untuk kepuasan pelanggan."
- Values:
  - **Responsive:** respond well within working hours, customer satisfaction is the priority.
  - **Quality:** goods are guaranteed and of good quality, from packaging to shipping.
  - **Support:** always support what the customer needs, don't hesitate to ask.
- Products section intro: "Produk kami dikembangkan dengan kualitas tinggi dengan berbagai jenis dan kategori unggulan yang diciptakan untuk kepuasan pelanggan."
- Footer: "Perusahaan alat kesehatan di Indonesia yang mengedepankan kepuasan pelanggan sebagai target utama perusahaan."
- Links: Shopee shop link, WhatsApp link (both **must be re-confirmed**).

**Missing, must be provided by the owner (track in `docs/CONTENT-TODO.md`)**
1. Logos (3), hero/banner photo, product photos.
2. Product list: name, category, brand, short description, specs, registration number (AKL/AKD/PKRT), price or "contact for price".
3. About Us text, vision and mission.
4. Confirmed address, phone, email for inquiries, WhatsApp number (international format), Shopee URL.
5. Single named approver for design and content.

Seed the database with **clearly fake demo data** (flagged `is_demo = true` or seeded only in local/staging) so the UI can be built. Production seeding uses only real, approved data.

---

## 6. Data model

All tables: `id`, `created_at`, `updated_at`. Use foreign keys and indexes. Slugs are unique.

**users** (Filament admins): name, email (unique), password, `is_admin` bool. Seed the first admin from env at deploy. Force a strong password.

**categories**: name, slug, description (nullable), sort_order, is_active.

**brands**: name, slug, logo_path (nullable), website_url (nullable), is_active. (Seed: Ofafa Beauty Care, Ofahusada, only if the owner confirms they should be catalog brands.)

**products**: category_id (FK), brand_id (nullable FK), name, slug, short_description (≤255), description (sanitized rich text), specifications (JSON array of `{label, value}`), registration_number (nullable), manufacturer (nullable), price (nullable decimal 14,2), show_price (bool, default false → display "Hubungi untuk harga"), is_featured, is_active, sort_order, meta_title (nullable), meta_description (nullable), `deleted_at` (soft delete).

**product_images**: product_id (FK, cascade), path, alt_text, sort_order, is_primary. Exactly one primary per product (enforce in app).

**inquiries**: product_id (nullable FK, nullOnDelete), name, company (nullable), phone, email (nullable), message, status (`new|contacted|closed`, default `new`), consent_at (timestamp, required), ip_hash (nullable, hashed, not raw IP), user_agent (nullable, truncated).

**pages**: slug (unique), title, body (sanitized rich text), meta_title, meta_description. Used for About and Privacy Policy so the owner can edit them.

**site_settings** (key/value, cached): company_name, tagline, address, phone, email, whatsapp_number, shopee_url, maps_embed_url, notification_email, ga4_id (optional), social links (optional).

---

## 7. Routes and pages

| URL | Purpose |
|---|---|
| `/` | Home: hero, intro, 3 values, featured products, brands, CTA, footer |
| `/produk` | Catalog list: search `?q=`, category `?kategori=`, brand `?merek=`, pagination, sort |
| `/produk/{slug}` | Product detail: gallery, specs, registration number, "Minta Penawaran" (WhatsApp + form) |
| `/tentang-kami` | About (from `pages`) |
| `/kontak` | Contact info, map, inquiry form |
| `POST /kontak`, `POST /produk/{slug}/penawaran` | Inquiry submission (rate limited) |
| `/kebijakan-privasi` | Privacy policy (from `pages`) |
| `/sitemap.xml`, `/robots.txt` | SEO |
| `/admin` | Filament panel |
| 404 / 500 | Branded error pages |

**Behaviors**
- Inactive products and categories return 404 publicly.
- Catalog URLs are indexable and canonical (strip tracking params). Search result pages (`?q=`) are `noindex`.
- WhatsApp button: `https://wa.me/{number}?text={urlencoded}` with text like "Halo, saya ingin meminta penawaran untuk {product} ({url})". Number comes from settings.
- Pick one preferred host (apex `ofamed.com` unless the owner says otherwise) and 301 the other (`www`) to it. HTTPS forced.

---

## 8. Admin (Filament) spec

- Resources: Products (with image repeater/uploader, drag-to-reorder, specs repeater, rich text, SEO fields, active/featured toggles), Categories, Brands, Pages, Inquiries (read, change status, search/filter, CSV export), Users.
- Settings page for `site_settings`.
- Dashboard widget: new inquiries count + latest 5.
- Admin UI in Indonesian. Clear labels, helper text for registration number and "Hubungi untuk harga".
- Validation: image types (jpg, png, webp), max 4 MB each, max 8 images per product. Slug auto-generated, editable, unique.
- Bulk actions: activate/deactivate, delete (soft).
- Non-technical user must be able to add a product in under 3 minutes (test this in UAT).

---

## 9. Inquiry flow

1. Visitor clicks "Minta Penawaran" on a product, or uses the contact form.
2. Form fields: name, phone, email (optional), company (optional), message, consent checkbox (link to privacy policy), honeypot field.
3. Server: validate, throttle (e.g. 5 per 10 minutes per IP), store inquiry, send email to `notification_email`. If email fails, still store the inquiry and log the error. Show a success message with a WhatsApp fallback link.
4. Optional anti-spam: Cloudflare Turnstile or similar. **ASK** before adding third-party scripts.
5. Admin sees it under Inquiries with status tracking.

---

## 10. Non-functional requirements

**SEO**: unique title and meta description per page, canonical URLs, Open Graph tags, `sitemap.xml` (home, catalog, products, categories, pages), `robots.txt` (block `/admin`), JSON-LD `Organization` (name, address, phone, logo) and `Product` (no `offers` unless a price is shown), breadcrumbs. Descriptive image alt text.

**Performance (targets, mobile, home + product page)**: Lighthouse Performance ≥ 90, Accessibility ≥ 95, Best Practices ≥ 95, SEO ≥ 95. WebP thumbnails, `loading="lazy"`, explicit image dimensions, font `display=swap`, minimal JS, HTTP caching headers, Laravel `config:cache`, `route:cache`, `view:cache` in production.

**Accessibility**: WCAG 2.1 AA as a baseline. Keyboard navigable, skip link, semantic landmarks, form labels and error messages, reduced-motion respect.

**Security**: `APP_DEBUG=false` in prod; `.env` never in web root; HTTPS only; security headers (HSTS, X-Content-Type-Options, Referrer-Policy, frame protections; CSP in report-only first); rate limit login and forms; hash passwords; validate and sanitize all input; sanitize rich text output; validate upload MIME and extension, store with random names; no directory listing; keep dependencies updated; `composer audit` clean at launch.

**Privacy**: collect only needed personal data in inquiries; consent checkbox; short privacy policy page (**owner or their counsel reviews**; you are not providing legal advice). Add a configurable retention note in the admin guide. Do not store raw IPs.

**Medical product content**: show registration numbers where provided. Make no health claims that the owner didn't supply.

---

## 11. Repository and conventions

```
/app                Laravel app (Models, Http, Filament resources, Services)
/database           migrations, factories, seeders (demo vs production seeders separated)
/resources/views    Blade (layouts, components, pages)
/resources/css|js   Tailwind entry, Alpine
/tests              Pest feature + unit tests
/design/reference   owner-provided mockup screenshots (read-only)
/docs               PLAN.md, ENVIRONMENT.md, DEPLOYMENT.md, ADMIN-GUIDE.md, CONTENT-TODO.md, RESTORE.md
/.github/workflows  ci.yml (tests, pint, build), optional deploy.yml
PROGRESS.md         live status (see section 16)
CLAUDE.md           short project brief + rules (generated from sections 0–3)
.env.example        all keys, no secrets
```

- Branching: `main` is deployable. Feature branches → PR → CI green → merge. Deploy from tags (`v1.0.0`).
- Services/actions for business logic (inquiry creation, image processing); keep controllers thin.
- Form Requests for validation. Policies for admin authorization.
- Demo data seeder must refuse to run when `APP_ENV=production`.

---

## 12. Phases, tasks, acceptance criteria

### Phase 0: Discovery and environment gate 🚧
No application code yet.
- [ ] Confirm hosting renewal status and expiry date. **ASK** the owner if renewal isn't confirmed.
- [ ] Inspect hosting capabilities (ask the owner to share screenshots or output where you can't see it): PHP version and extensions (`mbstring`, `openssl`, `pdo_mysql`, `gd` or `imagick` with WebP, `zip`, `fileinfo`, `intl`), Composer availability, SSH access, Git deployment, MySQL database creation, cron jobs, mailbox/SMTP, upload and memory limits, document-root options.
- [ ] Check DNS: the `@` A record should point to the hosting IP (`153.92.11.164`, verify in hPanel). Note the `www` record. Find out why the domain connection is stuck and fix or document.
- [ ] Check for a reachable subdomain for staging (e.g. `staging.ofamed.com`).
- [ ] Choose the deployment method (see section 13) and the backup destination.
- [ ] Create the GitHub repository under the client's account (or agree on transfer).
- [ ] Write `docs/ENVIRONMENT.md` with findings and the decisions above.

**Acceptance:** `ENVIRONMENT.md` exists; stack viability is confirmed or the fallback question has been asked. Human approves to proceed.

### Phase 1: Scaffold and tooling
- [ ] Laravel app, Filament panel at `/admin`, Tailwind + Alpine + Vite, Pest, Pint, (Larastan).
- [ ] `.env.example`, locale `id`, timezone `Asia/Jakarta`.
- [ ] GitHub Actions: install, Pint check, tests, build assets.
- [ ] Create `CLAUDE.md`, `docs/PLAN.md`, `PROGRESS.md`.
- [ ] Playwright MCP working (take a screenshot of the default page as a smoke test).

**Acceptance:** fresh clone → `composer install && npm ci && npm run build && php artisan migrate && php artisan test` works; CI green.

### Phase 2: Design system and static pages 🚧
- [ ] Implement tokens (colors, fonts, spacing, radius) for `CHOSEN_DESIGN` as Tailwind config and CSS variables.
- [ ] Layout, header/nav (mobile menu), footer, buttons, cards, form components, section components.
- [ ] Home, About, Contact (static content from section 5 and placeholders), 404/500.
- [ ] Playwright screenshots at 390, 768, 1280 px compared with `design/reference/`.

**Acceptance:** Home matches the reference closely at desktop and mobile. No horizontal scroll. Keyboard navigation works. Owner approves screenshots.

### Phase 3: Data layer and admin
- [ ] Migrations, models, relationships, factories, demo seeder, production seeder (admin user + settings + pages only).
- [ ] Filament resources and settings page per section 8.
- [ ] Image pipeline: validate, store, generate WebP thumbnails, delete files on removal.
- [ ] HTML sanitization for rich text.
- [ ] Feature tests for model rules, admin access, upload constraints.

**Acceptance:** admin can create a product with images in under 3 minutes; unauthorized users cannot reach `/admin`; tests pass.

### Phase 4: Public catalog and inquiries 🚧
- [ ] Catalog list with search, filters, pagination, sorting, empty state.
- [ ] Product detail with gallery, specs, registration number, price/"Hubungi untuk harga", related products.
- [ ] WhatsApp quote button and inquiry form; storage, email, throttling, honeypot, success/error states.
- [ ] Inquiry inbox in admin.
- [ ] Pest tests: list/filter/search, 404 for inactive, inquiry validation and rate limit, WhatsApp link generation.
- [ ] Design catalog and detail pages (not in the mockups). Owner reviews screenshots.

**Acceptance:** full visitor journey works on mobile and desktop: browse → product → quote via WhatsApp or form → admin sees the inquiry and receives the email. Owner approves.

### Phase 5: SEO, accessibility, performance, security
- [ ] Meta tags, canonical, OG, JSON-LD, sitemap, robots.
- [ ] Security headers, rate limits, upload hardening, `composer audit`, `npm audit`.
- [ ] Privacy policy page + consent wiring.
- [ ] Lighthouse and accessibility audits (axe via Playwright if available). Fix findings.

**Acceptance:** targets in section 10 met on home and a product page, or deviations are documented with reasons.

### Phase 6: QA and UAT 🚧
- [ ] Cross-device checks via Playwright (viewport sizes) and a manual note for real Android/iOS testing by the owner.
- [ ] Full test suite green. Proofread all Indonesian copy.
- [ ] UAT checklist with the owner: add/edit/delete product, change a setting, handle an inquiry, edit About text.
- [ ] Resolve revision list (within the agreed number of revision rounds).

**Acceptance:** owner signs off on UAT in writing (chat message is fine).

### Phase 7: Staging deploy and dry run
- [ ] Deploy to the staging subdomain with `noindex` and basic auth.
- [ ] Run migrations, production seeders, import real content provided by the owner.
- [ ] Test mail delivery from the server, file uploads, image generation, scheduler/cron.
- [ ] Take a backup and **perform a test restore** (see `docs/RESTORE.md`).
- [ ] Write `docs/DEPLOYMENT.md` as an exact runbook from what you actually did.

**Acceptance:** staging behaves like production would; backup restore proven; runbook reproducible.

### Phase 8: Production deploy and go-live 🚧
Follow section 13. Get explicit human go-ahead before switching DNS or deploying to the live document root.
- [ ] Final backup of anything existing on the hosting.
- [ ] Deploy, migrate, link storage, cache config/routes/views.
- [ ] DNS correct, SSL active, HTTPS redirect, host canonicalization.
- [ ] Smoke test on the live URL from a different network (mobile data).
- [ ] Submit sitemap in Google Search Console; install GA4 only if the owner opted in.

**Acceptance:** `https://ofamed.com` loads over HTTPS from outside the hosting network; inquiry test succeeds; no errors in logs.

### Phase 9: Handover and maintenance setup
- [ ] Admin account in the **client's name**. Remove or transfer any developer-only access.
- [ ] Credentials (hosting, domain, GitHub, SMTP, DB) shared via the client's password manager. Never in the repo or chat logs.
- [ ] `docs/ADMIN-GUIDE.md`: one page, screenshots, plain Indonesian (how to add a product, edit text, view inquiries).
- [ ] Automated backups running (files + DB), copy stored off-server, restore tested.
- [ ] Renewal dates for hosting and domain written down and put in the client's calendar.
- [ ] Optional: monthly maintenance checklist (updates, backup check, uptime monitor).
- [ ] Short handover session with the owner.

**Acceptance:** the client can operate the site without the developer, and every credential and renewal date is in their hands.

---

## 13. Deployment runbook (fill in details during Phase 0 and 7)

**Environments:** local → staging (`staging.ofamed.com`, noindex + basic auth) → production (`ofamed.com`).

**Production `.env` essentials:** `APP_ENV=production`, `APP_DEBUG=false`, `APP_URL=https://ofamed.com`, `APP_KEY` generated once and backed up securely, DB credentials, `MAIL_*` SMTP settings, `SESSION_SECURE_COOKIE=true`, `QUEUE_CONNECTION=sync` (unless validated otherwise), `LOG_LEVEL=warning`.

**Release steps (adapt to the chosen method)**
1. Tag release, CI builds assets, tests pass.
2. Backup DB and `storage/app/public` before touching production.
3. Upload code (Git pull on server, or CI artifact via SSH/SFTP, or zip upload). Include `vendor/` if Composer can't run on the server.
4. `php artisan migrate --force` (or import SQL if there is no CLI; document it).
5. `php artisan storage:link` (or equivalent copy/symlink if symlinks are blocked).
6. `php artisan config:cache route:cache view:cache` (and `filament:optimize` if available).
7. Permissions on `storage` and `bootstrap/cache`.
8. Smoke test: home, catalog, a product, contact form, admin login, image upload.
9. Rollback plan: keep the previous release folder/zip and the pre-deploy DB dump; document the exact rollback commands.

**DNS/SSL checklist**
- A record `@` → hosting IP; `www` handled per the canonical-host decision.
- Wait for propagation (use a public DNS checker), then enable SSL in hPanel and force HTTPS.
- Re-check that email-related DNS records (if any exist) are untouched.

**`.htaccess`:** HTTPS redirect, www/apex canonicalization, block access to dotfiles, `.env`, `storage`, `vendor` if inside the web root.

---

## 14. Backup and maintenance

- Use a backup package (e.g. `spatie/laravel-backup`) or a script: **DB dump + uploads**, weekly at minimum, retention 4–8 copies.
- Store a copy **off the hosting** (Google Drive, S3-compatible storage, or similar, decided in Phase 0). Hostinger's own backups were empty in the past, so do not rely on them.
- Alert on backup failure (email).
- Maintenance checklist (monthly): `composer outdated` / security updates, test suite, uptime check, backup verification, renewal dates.
- Recommend an uptime monitor (free tier) on the home page and `/produk`.

---

## 15. Definition of Done (project)

- [ ] All phases accepted; owner sign-off recorded.
- [ ] Tests and CI green; `composer audit` clean at launch.
- [ ] Lighthouse/accessibility targets met or documented.
- [ ] No placeholders left in production, or each one is listed in `CONTENT-TODO.md` and approved by the owner.
- [ ] Backups run and restore tested.
- [ ] Docs complete: `ENVIRONMENT.md`, `DEPLOYMENT.md`, `ADMIN-GUIDE.md`, `RESTORE.md`, `CONTENT-TODO.md`.
- [ ] Credentials and renewal dates handed to the client.

---

## 16. `PROGRESS.md` template

```markdown
# Progress: ofamed.com rebuild
Last updated: YYYY-MM-DD

## Current phase
Phase X: <name>  |  Status: not started | in progress | blocked | awaiting approval

## Decisions log
- YYYY-MM-DD: <decision> (why)

## Phase checklist
- [ ] Phase 0 Discovery  - [ ] Phase 1 Scaffold  - [ ] Phase 2 Design/static  - [ ] Phase 3 Data/admin
- [ ] Phase 4 Catalog/inquiries  - [ ] Phase 5 Hardening  - [ ] Phase 6 QA/UAT  - [ ] Phase 7 Staging
- [ ] Phase 8 Production  - [ ] Phase 9 Handover

## Open questions for the owner
- <question> (asked on YYYY-MM-DD)

## Known issues / tech debt
- <issue>

## Next 3 tasks
1. ...
```

---

## 17. Questions to ask the human (collect answers early)

1. Which design option (A/B/C) did the client choose? Can you export the mockup screenshots into `design/reference/`?
2. Is the hosting renewed, and until when? Who pays for renewals?
3. Preferred canonical address: `ofamed.com` or `www.ofamed.com`?
4. Real product list, photos, registration numbers, brand logos: who provides them and by when?
5. Which email receives inquiries? Which WhatsApp number? Current Shopee link?
6. Are Ofafa Beauty Care and Ofahusada catalog brands, sister companies, or both?
7. Does the client want Google Analytics, and any third-party anti-spam script?
8. Where should off-server backups go (Google Drive account, other)?
9. Who is the single approver for design and content decisions?
10. Does the client have someone who reviews the privacy policy text?
