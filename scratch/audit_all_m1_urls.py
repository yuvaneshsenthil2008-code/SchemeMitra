import json
import urllib.request
import urllib.parse
import urllib.error
import ssl
import socket
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M1_PATH = os.path.join(PROJECT_ROOT, "modules", "M1_data", "opportunity_master.json")

def check_url(url, timeout=10):
    if not url or not isinstance(url, str) or not url.strip():
        return {
            "status": "MANUAL_VERIFICATION_REQUIRED",
            "http_code": None,
            "error": "Empty or missing URL",
            "final_url": None
        }

    url = url.strip()
    
    # Custom SSL Context allowing fallback for government SSL certificate chain issues
    ctx_strict = ssl.create_default_context()
    ctx_relaxed = ssl.create_default_context()
    ctx_relaxed.check_hostname = False
    ctx_relaxed.verify_mode = ssl.CERT_NONE

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5'
    }

    parsed = urllib.parse.urlparse(url)
    hostname = parsed.hostname
    if not hostname:
        return {
            "status": "MANUAL_VERIFICATION_REQUIRED",
            "http_code": None,
            "error": "Invalid URL structure",
            "final_url": None
        }

    # 1. DNS Resolution Check
    try:
        socket.gethostbyname(hostname)
    except socket.gaierror as e:
        return {
            "status": "BROKEN_DNS",
            "http_code": None,
            "error": f"DNS Resolution Failed: {str(e)}",
            "final_url": None
        }
    except Exception as e:
        return {
            "status": "BROKEN_DNS",
            "http_code": None,
            "error": f"DNS Error: {str(e)}",
            "final_url": None
        }

    # Custom opener to follow redirects and capture final URL
    class RedirectHandler(urllib.request.HTTPRedirectHandler):
        def __init__(self):
            self.final_url = None
            self.redirect_count = 0

        def redirect_request(self, req, fp, code, msg, headers, newurl):
            self.final_url = newurl
            self.redirect_count += 1
            return super().redirect_request(req, fp, code, msg, headers, newurl)

    # 2. Try HTTP Request with strict SSL context first, then relaxed SSL
    for ctx, ssl_mode in [(ctx_strict, "strict"), (ctx_relaxed, "relaxed")]:
        handler = RedirectHandler()
        opener = urllib.request.build_opener(handler, urllib.request.HTTPSHandler(context=ctx))
        req = urllib.request.Request(url, headers=headers)
        
        try:
            with opener.open(req, timeout=timeout) as response:
                final_dest = handler.final_url or response.geturl()
                code = response.getcode()

                # Normalize URLs for comparison (strip trailing slashes, lower case scheme/host)
                norm_orig = url.rstrip('/')
                norm_dest = final_dest.rstrip('/')

                if norm_orig == norm_dest or norm_orig + "/" == norm_dest:
                    return {
                        "status": "VALID",
                        "http_code": code,
                        "error": None,
                        "final_url": final_dest,
                        "ssl_mode": ssl_mode
                    }
                else:
                    return {
                        "status": "VALID_REDIRECT",
                        "http_code": code,
                        "error": None,
                        "final_url": final_dest,
                        "ssl_mode": ssl_mode
                    }
        except urllib.error.HTTPError as e:
            code = e.code
            final_dest = e.url if hasattr(e, 'url') else None
            if code == 404:
                return {"status": "BROKEN_404", "http_code": code, "error": "404 Not Found", "final_url": final_dest}
            elif code in (500, 502, 503, 504):
                return {"status": "SERVER_ERROR", "http_code": code, "error": f"Server Error {code}", "final_url": final_dest}
            elif code in (401, 403):
                # 403 Forbidden on government sites often means bot blocking or geo-blocking
                return {"status": "MANUAL_VERIFICATION_REQUIRED", "http_code": code, "error": f"HTTP {code} Forbidden/Blocked", "final_url": final_dest}
            else:
                return {"status": "MANUAL_VERIFICATION_REQUIRED", "http_code": code, "error": f"HTTP Error {code}", "final_url": final_dest}
        except urllib.error.URLError as e:
            if isinstance(e.reason, socket.timeout):
                return {"status": "TIMEOUT", "http_code": None, "error": "Connection Timed Out", "final_url": None}
            elif "ssl" in str(e.reason).lower() and ssl_mode == "strict":
                continue # Retry with relaxed SSL context for government self-signed / expired certs
            else:
                return {"status": "MANUAL_VERIFICATION_REQUIRED", "http_code": None, "error": f"URL Error: {str(e.reason)}", "final_url": None}
        except socket.timeout:
            return {"status": "TIMEOUT", "http_code": None, "error": "Socket Timed Out", "final_url": None}
        except Exception as e:
            return {"status": "MANUAL_VERIFICATION_REQUIRED", "http_code": None, "error": f"Unexpected Error: {str(e)}", "final_url": None}

    return {"status": "MANUAL_VERIFICATION_REQUIRED", "http_code": None, "error": "SSL Verification Failure", "final_url": None}


def run_audit():
    with open(M1_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    results = []
    print(f"Loaded {len(data)} opportunities from opportunity_master.json")
    print("Beginning automated URL audit...\n")

    for idx, item in enumerate(data, 1):
        opp_id = item.get("Opportunity_ID") or item.get("opportunity_id") or f"OPP_{idx:03d}"
        name = item.get("Opportunity_Name") or item.get("opportunity_name") or ""
        url = item.get("Official_Source_URL") or item.get("official_source_url") or item.get("Application_URL") or ""
        last_verified = item.get("Last_Verified") or item.get("last_verified") or ""

        print(f"[{idx}/{len(data)}] Checking {opp_id}: {name[:40]}... ({url})")
        res = check_url(url)
        res["opportunity_id"] = opp_id
        res["opportunity_name"] = name
        res["stored_url"] = url
        res["last_verified"] = last_verified
        results.append(res)

    out_file = os.path.join(PROJECT_ROOT, "scratch", "url_audit_live_results.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\nAudit completed! Results saved to {out_file}")

if __name__ == "__main__":
    run_audit()
