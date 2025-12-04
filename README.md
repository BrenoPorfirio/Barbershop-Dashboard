<h1 align="center">💈 Barbershop Dashboard </h1>

<p align="center">
  <a href="#tecnologias">Tecnologias</a>&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
  <a href="#projeto">Projeto</a>&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
  <a href="#execucao">Execução</a>&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
  <a href="#gerar-dados-ficticios">Gerar Dados Fictícios</a>&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
  <a href="#objetivos">Objetivos</a>
</p>

<br>

<p align="center">
  <img width="100%" alt="Barbershop Dashboard" src="https://github.com/user-attachments/assets/b89b59e5-05e3-48cd-8688-a54255ea0ee3">
</p>

---

## 🚀 Tecnologias

Esse projeto foi desenvolvido utilizando:

- **Python**
- **Streamlit**
- **Pandas**
- **NumPy**
- **Plotly**
- **ARIMA**
- **Git & GitHub**

---

## 💻 Projeto

O **Barbershop Dashboard** é um painel interativo criado para facilitar a visualização de métricas importantes de uma barbearia, incluindo:

- ✔️ Atendimentos semanais e mensais
- ✔️ Custos detalhados
- ✔️ Lucros reais e projetados
- ✔️ Comparação entre anos (2025 vs. 2026)
- ✔️ Mapa de calor dos atendimentos
- ✔️ Estatísticas dos melhores dias e semanas

O sistema também permite **gerar automaticamente dados fictícios reais**, simulando períodos anuais completos.

---

## 📝 Execução

Siga os passos abaixo para rodar o projeto localmente:

### **1️⃣ Clone o repositório**

```bash
git clone https://github.com/BrenoPorfirio/Barbershop-Dashboard.git
```

### **2️⃣ Acesse o diretório**

```bash
  cd Barbershop-Dashboard
```

### **3️⃣ Instale as dependências**

```bash
  pip install -r requirements.txt
```

### **4️⃣ Execute o dashboard Streamlit**

```bash
  streamlit run app.py
```

### **4️⃣ Outra opção de execução**

```bash
  python -m streamlit run app.py
```

---

## 📈 Gerar Dados Fictícios

Se quiser regenerar completamente os dados de 2026, execute o script responsável:

```bash
  python data/generate_fictitious_data.py
```

Esse comando cria automaticamente:

data/table_2026.csv

🔹 Os dados incluem variações reais, picos em meses específicos e limites bem definidos.
🔹 Ideal para simulação e testes do dashboard.

---

## 🎯 Objetivo

Este dashboard foi desenvolvido para auxiliar barbearias e pequenos negócios a monitorar:

Desempenho operacional

Crescimento mês a mês

Análise financeira

Fluxo semanal de atendimento

Fornecendo visualizações avançadas e estatísticas de forma simples e intuitiva.
