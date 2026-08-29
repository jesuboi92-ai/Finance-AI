-- Initialize database tables and seed data

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Insert sample users
INSERT INTO users (id, email, username, full_name, hashed_password, is_active, is_admin, role, department, created_at, updated_at)
VALUES 
  (uuid_generate_v4(), 'admin@logistics.com', 'admin', 'System Admin', crypt('admin123', gen_salt('bf')), true, true, 'admin', 'management', now(), now()),
  (uuid_generate_v4(), 'manager@logistics.com', 'manager', 'Warehouse Manager', crypt('manager123', gen_salt('bf')), true, false, 'manager', 'warehouse', now(), now()),
  (uuid_generate_v4(), 'driver@logistics.com', 'driver', 'Transport Driver', crypt('driver123', gen_salt('bf')), true, false, 'operator', 'transport', now(), now());

-- Insert sample inventory items
INSERT INTO inventory (id, sku, product_name, description, quantity, reserved_quantity, available_quantity, reorder_level, unit_price, location, category, created_at, updated_at)
VALUES 
  (uuid_generate_v4(), 'SKU001', 'Electronic Component A', 'High-tech component', 100, 20, 80, 10, 25.99, 'A1', 'electronics', now(), now()),
  (uuid_generate_v4(), 'SKU002', 'Packaging Material B', 'Cardboard boxes', 500, 100, 400, 50, 2.50, 'A2', 'materials', now(), now()),
  (uuid_generate_v4(), 'SKU003', 'Office Supply C', 'Paper sheets', 1000, 200, 800, 100, 0.05, 'B1', 'supplies', now(), now());

-- Insert sample customers
INSERT INTO customers (id, customer_name, customer_type, email, phone, address, city, postal_code, country, preferred_contact, is_active, created_at, updated_at)
VALUES 
  (uuid_generate_v4(), 'Tech Solutions Inc', 'business', 'contact@techsol.com', '+1234567890', '123 Tech Street', 'San Francisco', '94105', 'USA', 'email', true, now(), now()),
  (uuid_generate_v4(), 'Retail Store Ltd', 'business', 'info@retailstore.com', '+0987654321', '456 Market Ave', 'New York', '10001', 'USA', 'phone', true, now(), now());

-- Insert sample message templates
INSERT INTO message_templates (id, template_name, template_type, channel, subject, body, is_active, created_at, updated_at)
VALUES 
  (uuid_generate_v4(), 'Delivery Confirmation', 'confirmation', 'email', 'Your order has been delivered', '<p>Hello {{customer_name}},</p><p>Your order {{order_number}} has been successfully delivered.</p>', true, now(), now()),
  (uuid_generate_v4(), 'Delay Notification', 'delay', 'sms', null, 'Hello {{customer_name}}, your order {{order_number}} will be delayed due to {{reason}}. We apologize for the inconvenience.', true, now(), now()),
  (uuid_generate_v4(), 'Order Update', 'update', 'email', 'Order {{order_number}} status update', '<p>Your order status has been updated to {{status}}.</p>', true, now(), now());
