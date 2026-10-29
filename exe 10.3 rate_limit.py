import ipaddress
import json
import time
import urllib.error
import urllib.request

API_URL = "http://ip-api.com/json/{ip}?fields=status,message,city,country,countryCode,isp,org,proxy,hosting,query"
MAX_TENTATIVAS = 4
BACKOFF_BASE = 1.0  # segundos: 1, 2, 4, 8...


IPS_SUSPEITOS = {"185.220.101.1"}


class EnriquecedorIP:
    def __init__(self, sleep=time.sleep):
        self.cache = {}             
        self.sleep = sleep          
        self.stats = {"http": 0, "cache": 0, "internos": 0, "erros": 0, "retries": 0}

   
    @staticmethod
    def classificar(ip: str) -> str:
        """Retorna 'INVALIDO', 'INTERNO' ou 'EXTERNO'."""
        try:
            obj = ipaddress.ip_address(ip)
        except ValueError:
            return "INVALIDO"
        if (obj.is_private or obj.is_loopback or obj.is_link_local
                or obj.is_reserved or obj.is_multicast):
            return "INTERNO"
        return "EXTERNO"

    # ---------- chamada HTTP com backoff ----------
    def _consultar_api(self, ip: str) -> dict:
        url = API_URL.format(ip=ip)
        for tentativa in range(1, MAX_TENTATIVAS + 1):
            try:
                with urllib.request.urlopen(url, timeout=5) as resp:
                    self.stats["http"] += 1
                    return json.loads(resp.read().decode())
            except urllib.error.HTTPError as e:
                if e.code == 429 and tentativa < MAX_TENTATIVAS:
                    # respeita Retry-After se existir, senão backoff exponencial
                    espera = float(e.headers.get("Retry-After", BACKOFF_BASE * 2 ** (tentativa - 1)))
                    print(f"  [429] {ip}: aguardando {espera:.0f}s "
                          f"(tentativa {tentativa}/{MAX_TENTATIVAS})")
                    self.stats["retries"] += 1
                    self.sleep(espera)
                    continue
                raise
            except (urllib.error.URLError, TimeoutError):
                if tentativa < MAX_TENTATIVAS:
                    self.sleep(BACKOFF_BASE * 2 ** (tentativa - 1))
                    self.stats["retries"] += 1
                    continue
                raise
        raise RuntimeError("Tentativas esgotadas")

   
    def enriquecer(self, ip: str) -> dict:
        tipo = self.classificar(ip)

        if tipo == "INVALIDO":
            self.stats["erros"] += 1
            return {"ip": ip, "tipo": tipo, "fonte": "validação", "detalhe": "IP inválido"}

        if tipo == "INTERNO":
            self.stats["internos"] += 1
            return {"ip": ip, "tipo": tipo, "fonte": "local", "detalhe": "Rede Interna (não consultado)"}

        if ip in self.cache:
            self.stats["cache"] += 1
            return {**self.cache[ip], "fonte": "cache"}

        try:
            dados = self._consultar_api(ip)
        except Exception as e:
            self.stats["erros"] += 1
            return {"ip": ip, "tipo": tipo, "fonte": "erro", "detalhe": f"falha na consulta: {e}"}

        if dados.get("status") != "success":
            self.stats["erros"] += 1
            return {"ip": ip, "tipo": tipo, "fonte": "erro", "detalhe": dados.get("message", "erro")}

        suspeito = (ip in IPS_SUSPEITOS or dados.get("proxy") or dados.get("hosting"))
        resultado = {
            "ip": ip,
            "tipo": tipo,
            "cidade": dados.get("city"),
            "pais": dados.get("countryCode"),
            "org": dados.get("org") or dados.get("isp"),
            "suspeito": bool(suspeito),
            "fonte": "http",
        }
        self.cache[ip] = resultado
        return resultado

   
    @staticmethod
    def formatar(r: dict) -> str:
        if r["fonte"] in ("erro", "validação", "local"):
            return f"{r['ip']:<16}-> {r['detalhe']}" + ("" if r["fonte"] != "local" else "")
        local = f"{r['cidade']} / {r['pais']} / {r['org']}"
        if r["fonte"] == "cache":
            return f"{r['ip']:<16}-> [CACHE] sem nova chamada HTTP"
        marca = "EXTERNO, suspeito" if r["suspeito"] else "EXTERNO"
        return f"{r['ip']:<16}-> {local} ({marca})"

    def relatorio(self, ips: list) -> list:
        resultados = []
        for ip in ips:
            r = self.enriquecer(ip)
            print(self.formatar(r))
            resultados.append(r)
        s = self.stats
        print("\n=== Resumo ===")
        print(f"Consultas HTTP: {s['http']} | Cache hits: {s['cache']} | "
              f"Internos: {s['internos']} | Erros: {s['erros']} | Retries: {s['retries']}")
        return resultados


if __name__ == "__main__":
    ips = ["8.8.8.8", "1.1.1.1", "185.220.101.1", "192.168.1.10", "8.8.8.8"]
    EnriquecedorIP().relatorio(ips)
