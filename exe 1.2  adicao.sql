INSERT INTO alertas (tipo, ip_origem, severidade, status) VALUES
('Tentativa de Login Falha', '192.168.1.50', 'alta', 'aberto'),
('Uso Alto de CPU', '10.0.0.15', 'media', 'aberto'),
('Acesso Não Autorizado', '172.16.0.5', 'critica', 'aberto');

SELECT * FROM alertas 
WHERE severidade = 'alta';

UPDATE alertas 
SET status = 'resolvido' 
WHERE id = 1;

SELECT severidade, COUNT(*) AS total 
FROM alertas 
GROUP BY severidade;
