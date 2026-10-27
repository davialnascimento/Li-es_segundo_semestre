INSERT INTO alertas (tipo, severidade, ip_origem) VALUES
('BRUTE_FORCE', 'critica', '185.220.101.1'),
('BRUTE_FORCE', 'alta',    '185.220.101.1'),
('BRUTE_FORCE', 'alta',    '185.220.101.1'),
('BRUTE_FORCE', 'media',   '45.33.32.156'),
('PORT_SCAN',   'critica', '45.33.32.156'),
('PORT_SCAN',   'alta',    '45.33.32.156'),
('PORT_SCAN',   'media',   '192.168.1.50'),
('XSS',         'critica', '192.168.1.50'),
('XSS',         'baixa',   '10.0.0.15'),
('SQLI',        'alta',    '10.0.0.15');

SELECT severidade, COUNT(*) AS total
FROM alertas
GROUP BY severidade
ORDER BY total DESC;

