-- Seed data for Personal Finance Tracker
-- Note: Expenses are stored as negative amounts, Income as positive amounts.
-- auto_tagged: 1 for auto-categorized, 0 for manually tagged or reclassified.

INSERT INTO transactions (description, amount, transaction_type, category, auto_tagged, timestamp) VALUES
-- August 2026
('Monthly Salary', 5000.00, 'income', 'Salary', 1, '2026-08-01 09:00:00'),
('Apartment Rent', -1200.00, 'expense', 'Rent', 1, '2026-08-02 10:00:00'),
('McDonalds Lunch', -15.50, 'expense', 'Food', 1, '2026-08-03 12:30:00'),
('Uber to Airport', -35.00, 'expense', 'Travel', 0, '2026-08-05 15:45:00'),
('Electricity Bill', -85.20, 'expense', 'Utilities', 1, '2026-08-08 11:20:00'),
('Netflix Subscription', -14.99, 'expense', 'Entertainment', 1, '2026-08-15 08:00:00'),
('Starbucks Coffee', -7.50, 'expense', 'Food', 1, '2026-08-20 16:10:00'),

-- September 2026
('Monthly Salary', 5000.00, 'income', 'Salary', 1, '2026-09-01 09:00:00'),
('Apartment Rent', -1200.00, 'expense', 'Rent', 1, '2026-09-02 10:00:00'),
('Swiggy Dinner Order', -28.40, 'expense', 'Food', 1, '2026-09-04 20:15:00'),
('Metro Card Recharge', -50.00, 'expense', 'Transport', 1, '2026-09-07 09:30:00'),
('Internet Bill Wifi', -60.00, 'expense', 'Utilities', 1, '2026-09-12 14:00:00'),
('Spotify Premium', -9.99, 'expense', 'Entertainment', 1, '2026-09-15 08:00:00'),
('Freelance Bonus', 750.00, 'income', 'Salary', 0, '2026-09-22 17:30:00'),
('Flight Tickets to Vacation', -320.00, 'expense', 'Travel', 0, '2026-09-25 18:00:00'),

-- October 2026
('Monthly Salary', 5000.00, 'income', 'Salary', 1, '2026-10-01 09:00:00'),
('Apartment Rent', -1200.00, 'expense', 'Rent', 1, '2026-10-02 10:00:00'),
('Grocery Store Market', -112.80, 'expense', 'Food', 1, '2026-10-04 11:00:00'),
('Uber Ride to Office', -18.50, 'expense', 'Transport', 1, '2026-10-06 08:45:00'),
('Cinema Movie Tickets', -32.00, 'expense', 'Entertainment', 1, '2026-10-08 19:30:00');
