import pandas as pd

# Dados v5 - Incluindo Descrições para o Seletor
data = [
    {
        "Projeto": "2024.0824", "Descricao": "Climatização Casa de Força",
        "Cliente": "BP", "Cidade": "Pedro Afonso", "Status": "Finalizado",
        "Vendido": 882000, "Faturado": 1764000, "Impostos": 172254.60,
        "Mat_Orc": 287248, "Mat_Real": 245067, "Desp_Orc": 149758, "Desp_Real": 178732,
        "HH_Orc_Vlr": 87312, "HH_Real_Vlr": 16271, "HH_Orc_Qtd": 1600, "HH_Real_Qtd": 350, "Conclusao_%": 100
    },
    {
        "Projeto": "2025.0452", "Descricao": "Infra Gás GLP Pesquisa",
        "Cliente": "Bayer", "Cidade": "Uberlândia", "Status": "Finalizado",
        "Vendido": 20000, "Faturado": 20000, "Impostos": 3906.00,
        "Mat_Orc": 3350, "Mat_Real": 2100, "Desp_Orc": 2956, "Desp_Real": 1467,
        "HH_Orc_Vlr": 4957, "HH_Real_Vlr": 457, "HH_Orc_Qtd": 100, "HH_Real_Qtd": 12, "Conclusao_%": 100
    },
    {
        "Projeto": "2025.0607", "Descricao": "Elétrica Refeitório",
        "Cliente": "Engetrad", "Cidade": "Pedro Afonso", "Status": "Finalizado",
        "Vendido": 66000, "Faturado": 66000, "Impostos": 12889.80,
        "Mat_Orc": 11290, "Mat_Real": 5139, "Desp_Orc": 13771, "Desp_Real": 1356,
        "HH_Orc_Vlr": 14586, "HH_Real_Vlr": 2458, "HH_Orc_Qtd": 280, "HH_Real_Qtd": 50, "Conclusao_%": 100
    },
    {
        "Projeto": "2025.1102", "Descricao": "Reforma Painéis Elétricos",
        "Cliente": "Bayer", "Cidade": "Uberlândia", "Status": "Em andamento",
        "Vendido": 45000, "Faturado": 20000, "Impostos": 8775.00,
        "Mat_Orc": 12000, "Mat_Real": 13500, "Desp_Orc": 3000, "Desp_Real": 2800,
        "HH_Orc_Vlr": 8000, "HH_Real_Vlr": 5500, "HH_Orc_Qtd": 200, "HH_Real_Qtd": 140, "Conclusao_%": 70
    },
    {
        "Projeto": "2025.0888", "Descricao": "Iluminação LED Industrial",
        "Cliente": "Bayer", "Cidade": "Rio Verde", "Status": "Em andamento",
        "Vendido": 150000, "Faturado": 50000, "Impostos": 29250.00,
        "Mat_Orc": 70000, "Mat_Real": 72000, "Desp_Orc": 10000, "Desp_Real": 14000,
        "HH_Orc_Vlr": 25000, "HH_Real_Vlr": 28000, "HH_Orc_Qtd": 500, "HH_Real_Qtd": 600, "Conclusao_%": 90
    },
    {
        "Projeto": "2025.2020", "Descricao": "Subestação de Energia",
        "Cliente": "Vale", "Cidade": "Canaã", "Status": "Em andamento",
        "Vendido": 300000, "Faturado": 100000, "Impostos": 58500.00,
        "Mat_Orc": 140000, "Mat_Real": 110000, "Desp_Orc": 20000, "Desp_Real": 15000,
        "HH_Orc_Vlr": 50000, "HH_Real_Vlr": 30000, "HH_Orc_Qtd": 1000, "HH_Real_Qtd": 400, "Conclusao_%": 45
    }
]

df = pd.DataFrame(data)
df.to_excel("dados_obras_v5.xlsx", index=False)
print("✅ Base de dados 'dados_obras_v5.xlsx' gerada!")
