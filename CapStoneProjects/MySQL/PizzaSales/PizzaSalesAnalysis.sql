create database PizzaSales;
use PizzaSales;
SELECT * FROM ORDER_DETAILS;
SELECT * FROM PIZZA_TYPES;
SELECT * FROM ORDERS;
SELECT * FROM PIZZAS;

-- RETRIVE THE TOTAL ORDER

select count(order_id) from orders;

-- RETRIVE TOTAL REVENUE GENERATED FROM PIZZA SALES

SELECT round(SUM(D.QUANTITY *P.PRICE),2)
as Total_Sales
FROM ORDER_DETAILS D
JOIN pizzas P ON p.pizza_id = D.pizza_id; 

-- IDENTIFY THE HIGHEST PRICED PIZZA 

SELECT pizza_types.name, pizzas.price
FROM
pizza_types
JOIN pizzas ON pizza_types.pizza_type_id =
pizzas.pizza_type_id
ORDER BY pizzas.price DESC LIMIT 1;

-- IDENTIFY THE MOST COMMON PIZZA SIZED ORDERED

SELECT pizzas.size,
COUNT(order_details.order_details_id) AS order_count
FROM pizzas
JOIN order_details ON pizzas.pizza_id = order_details.pizza_id
GROUP BY pizzas.size ORDER BY order_count DESC;

-- List the top 5 most ordered pizza types along with their quantities. 

SELECT pizza_types.name, SUM(order_details.quantity) AS
quantity FROM pizza_types
JOIN pizzas ON pizza_types.pizza_type_id =pizzas.pizza_type_id
JOIN order_details ON order_details.pizza_id =
pizzas.pizza_id GROUP BY pizza_types.name ORDER BY quantity DESC
LIMIT 5;

-- FIND THE TOTAL QUANTITY

SELECT PT.category,
SUM(D.quantity) AS QUANTITY
FROM pizza_types PT
JOIN pizzas P ON PT.pizza_type_id = P.pizza_type_id
JOIN order_details D ON D.pizza_id = P.pizza_id
GROUP BY PT.category;

-- DETERMINE THE DISTRIBUTION OF ORDERS BY HOUR OF THE DAY

SELECT
HOUR(order_time) AS hour, COUNT(order_id) AS order_id
FROM
orders
GROUP BY HOUR(order_time);

-- FIND THE CATAGORYWISE DISTRIBUTION OF PIZZAS 

SELECT
COUNT(name), category
FROM
pizza_types
GROUP BY category;

-- CALCULATE THE AVERAGE NUMBER OF PIZZAS ORDERED PER DAY

SELECT
ROUND(AVG(quantity), 0) as AVG_PER_DAY_PIZZA_ORDER
FROM
(SELECT O.date, SUM(D.quantity) AS
quantity
FROM
orders O
JOIN order_details D ON O.order_id = D.order_id
GROUP BY O.date) AS order_quantity;

-- DETERMINE THE TOP 3 MOST ORDERED PIZZA TYPES BASED ON REVENUE 

SELECT pizza_types.name,
SUM(pizzas.price * order_details.quantity) AS revenue
FROM
pizzas
JOIN pizza_types ON pizzas.pizza_type_id =
pizza_types.pizza_type_id
JOIN order_details ON order_details.pizza_id =
pizzas.pizza_id
GROUP BY pizza_types.name
ORDER BY revenue DESC
LIMIT 3;

-- CALCULATE THE PERCENTAGE CONTRIBUTION OF EACH POZZA TYPE TO TOTAL REVENUE 

SELECT pizza_types.category,
ROUND(SUM(pizzas.price * order_details.quantity) / (SELECT
SUM(order_details.quantity * pizzas.price)
FROM
order_details
JOIN pizzas ON order_details.pizza_id = pizzas.pizza_id) * 100, 2) AS revenue
FROM
pizza_types
JOIN pizzas ON pizza_types.pizza_type_id =
pizzas.pizza_type_id
JOIN order_details ON order_details.pizza_id =
pizzas.pizza_id
GROUP BY pizza_types.category
ORDER BY revenue DESC;

-- ANALYZE THE CUMULATIVE REVENUE GENERATED OVER TIME 

select order_date,
sum(revenue) over (order by order_date) as cm_revenue from
(select orders.order_date,
round(sum(order_details.quantity * pizzas.price),2) as revenue
from order_details join pizzas on order_details.pizza_id = pizzas.pizza_id 
join orders on orders.order_id = order_details.order_id 
group by orders.order_date) as sales;

-- DETERMINE THR TOP 3 MOST ORDERED PIZZA TYPES BASED ON REVENUEFOR EACH PIZZA CATAGORY

select name, revenue from (select category, name, revenue,
rank() over (partition by category order by revenue desc) as rn from
(select pizza_types.category, pizza_types.name, sum(order_details.quantity * pizzas.price) as revenue from pizza_types join pizzas on pizza_types.pizza_type_id = pizzas.pizza_type_id join order_details on order_details.pizza_id =
pizzas.pizza_id
group by pizza_types.category, pizza_types.name) as a) as b where rn<=3;
