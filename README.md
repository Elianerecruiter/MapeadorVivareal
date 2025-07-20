# Mapeador de Imóveis VivaReal - Barão Geraldo

Este projeto monitora anúncios de casas à venda em Barão Geraldo (Campinas/SP) no VivaReal, filtrando imóveis abaixo de R$ 1.000.000, e envia notificações por e-mail quando surgem novos anúncios.

## Como usar

1. **Clone o repositório**
2. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure as variáveis de ambiente:**
   - `EMAIL_FROM`: e-mail remetente (ex: mapeador.bot@gmail.com)
   - `EMAIL_PASSWORD`: senha do e-mail remetente (ou senha de app)
   - `EMAIL_TO`: e-mail destinatário
   - `SMTP_SERVER`: servidor SMTP (padrão: smtp.gmail.com)
   - `SMTP_PORT`: porta SMTP (padrão: 587)

4. **Execute o script:**
   ```bash
   python main.py
   ```

## Automação

Para rodar automaticamente (ex: via GitHub Actions), configure os secrets do repositório com as variáveis acima. 