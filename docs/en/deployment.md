# Deployment

## Build

```bash
python build.py
```

HTML is generated in the `public/` directory:

```text
public/
├── index.html            # listing page
├── entries/
│   └── <id>/
│       └── index.html   # detail page
├── static/              # CSS, JS
└── files/               # attached files (copied)
```

To change the output directory:

```bash
python build.py --output /var/www/html
```

## GitHub Pages

The included `.github/workflows/build.yml` automatically builds on push to `data/` or `files/` and deploys to the `gh-pages` branch.

Go to the repository Settings → Pages → Branch and select `gh-pages`.

## nginx

```bash
python build.py --output /var/www/scholist
```

Example nginx config:

```nginx
server {
    listen 80;
    server_name your-domain.example.com;
    root /var/www/scholist;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }
}
```

## Restricting access to attached files (nginx)

To password-protect or IP-restrict files under `files/`, the recommended approach is to use a `files/restricted/` subdirectory.

- Place public files at `files/foo.pdf`, restricted files at `files/restricted/bar.pptx`
- In YAML, just write `path: "files/restricted/bar.pptx"` — template-generated relative links resolve correctly
- `build.py` recursively copies `files/` into `public/files/` as-is, so no code changes are needed
- Apply access control only to `location /files/restricted/` in nginx

```nginx
# /files/ is public (no location block needed)
location /files/restricted/ {
    auth_basic "Restricted";
    auth_basic_user_file /etc/nginx/.htpasswd;
    # To combine with IP restriction:
    # satisfy any;   # OR condition (IP pass skips auth)
    # allow 203.0.113.0/24;
    # deny all;
}
```

> **GitHub Pages:** Server-side access control is not possible with static hosting.
> For files that need protection, host them on an external service and reference a limited-access URL via `files[].url` in the YAML.
