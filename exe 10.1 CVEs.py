
import requests

BASE_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"


def buscar_cve(cve_id):
    parametros = {"cveId": cve_id}

    try:
        resposta = requests.get(
            BASE_URL,
            params=parametros,
            timeout=10
        )

        if resposta.status_code == 404:
            print("CVE não encontrada")
            return

        resposta.raise_for_status()

        dados = resposta.json()
        vulnerabilidades = dados.get("vulnerabilities", [])

        if not vulnerabilidades:
            print("CVE não encontrada")
            return

        cve = vulnerabilidades[0]["cve"]

        # Extrair descrição, priorizando inglês
        descricoes = cve.get("descriptions", [])
        descricao = next(
            (d["value"] for d in descricoes
             if d.get("lang") == "en"),
            "Descrição indisponível"
        )

        # Priorizar CVSS 3.1, depois 3.0, 4.0 e 2.0
        metricas = cve.get("metrics", {})
        cvss = None

        for versao in (
            "cvssMetricV31",
            "cvssMetricV30",
            "cvssMetricV40",
            "cvssMetricV2"
        ):
            if metricas.get(versao):
                cvss = metricas[versao][0]["cvssData"]
                break

        print(cve_id)

        if cvss:
            score = cvss.get("baseScore", "N/A")
            severidade = cvss.get("baseSeverity", "N/A")
            print(f"  CVSS: {score} ({severidade})")
        else:
            print("  CVSS: indisponível")
            print("  Severidade: indisponível")

        print(f"  Descrição: {descricao}")

    except requests.exceptions.Timeout:
        print("Erro: tempo limite da requisição excedido.")

    except requests.exceptions.HTTPError as erro:
        if erro.response is not None and erro.response.status_code == 404:
            print("CVE não encontrada")
        else:
            print("Erro HTTP ao consultar a API do NVD.")

    except requests.exceptions.RequestException:
        print("Erro de conexão ao consultar a API do NVD.")

    except (ValueError, KeyError, IndexError, TypeError):
        print("Erro ao processar os dados retornados pela API.")


if __name__ == "__main__":
    buscar_cve("CVE-2021-44228")
