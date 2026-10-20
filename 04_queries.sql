-- Consulta 1: Listar usuarios con el nombre de su Rol
SELECT u.USER_ID, u.FULL_NAME, u.EMAIL, r.ROLE_NAME
FROM USERS u
JOIN ROLES r ON u.ROLE_ID = r.ROLE_ID;

-- Consulta 2: Listar equipos con el nombre de su Categoría
SELECT e.EQUIPMENT_ID, e.NAME AS EQUIPMENT, c.NAME AS CATEGORY, e.STATUS
FROM EQUIPMENT e
JOIN CATEGORIES c ON e.CATEGORY_ID = c.CATEGORY_ID;