1. Tabela de saldo bancário de clientes. 
2. Ingestão de 500 mil eventos de firewall por minuto num SOC.  
3. Cache de tokens de sessão de usuários logados. AP
4. Registro de quem autorizou cada transferência (auditoria). CP
5. Feed de indicadores de ameaça (IOCs) replicado em 5 regiões. AP

Repostas: 
1: CP, cistemas financeiros não podem tolerar inconcistências.
Se o sistema falhar ou a rede cair, o banco preferira recusar a transação ao saldo incorreto 
2: AP, O sistema não pode parar de receber logs de firewall porque um nó falhou ou perdeu conexão.
Podendo ser considerado a demora de alguns logs. 
3: AP, esse tipo de servidor prioriza a disponibilidade e a baixa latência.
4: CP não pode  pode haver divergência, perda de registros  sobre quem autorizou uma transferência financeira.
A consistência vem antes da disponibilidade.
5: AP, o importante é que cada região consiga consultar os IOCs rapidamente localmente.
Se uma região se desconectar, ela continua servindo sua base local (consistência eventual).
