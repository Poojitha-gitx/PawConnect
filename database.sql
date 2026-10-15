-- ============================================================
-- PawConnect - Pet Adoption Management System
-- DBMS Mini Project Schema & Demonstration Sample Dataset
-- Compatible with MySQL 8.0+ / MariaDB
-- ============================================================

CREATE DATABASE IF NOT EXISTS `pawconnect_db` 
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE `pawconnect_db`;

-- ------------------------------------------------------------
-- 1. Table: users
-- Core authentication and role-based user table
-- Roles: 'adopter', 'shelter', 'admin'
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `users` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `full_name` VARCHAR(100) NOT NULL,
    `email` VARCHAR(150) NOT NULL UNIQUE,
    `password_hash` VARCHAR(255) NOT NULL,
    `phone` VARCHAR(20) DEFAULT NULL,
    `address` TEXT DEFAULT NULL,
    `role` ENUM('adopter', 'shelter', 'admin') NOT NULL DEFAULT 'adopter',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 2. Table: shelters
-- Animal shelters and independent pet rescuers
-- Linked 1-to-1 with a user having role='shelter'
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `shelters` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL UNIQUE,
    `shelter_name` VARCHAR(150) NOT NULL,
    `license_number` VARCHAR(80) DEFAULT NULL,
    `city` VARCHAR(80) NOT NULL,
    `state` VARCHAR(80) NOT NULL,
    `address` TEXT NOT NULL,
    `phone` VARCHAR(20) NOT NULL,
    `email` VARCHAR(150) NOT NULL,
    `website` VARCHAR(255) DEFAULT NULL,
    `description` TEXT DEFAULT NULL,
    `is_verified` BOOLEAN NOT NULL DEFAULT FALSE,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_shelter_user` FOREIGN KEY (`user_id`) 
        REFERENCES `users`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 3. Table: admins
-- Platform administrators for moderating shelters & pet listings
-- Linked 1-to-1 with a user having role='admin'
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `admins` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL UNIQUE,
    `admin_code` VARCHAR(50) NOT NULL UNIQUE,
    `department` VARCHAR(100) DEFAULT 'Safety & Verification',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_admin_user` FOREIGN KEY (`user_id`) 
        REFERENCES `users`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 4. Table: pets
-- Pets registered by shelters available for adoption
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `pets` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `shelter_id` INT NOT NULL,
    `name` VARCHAR(80) NOT NULL,
    `species` ENUM('Dog', 'Cat', 'Rabbit', 'Bird', 'Other') NOT NULL DEFAULT 'Dog',
    `breed` VARCHAR(100) NOT NULL,
    `age_years` INT NOT NULL DEFAULT 1,
    `age_months` INT NOT NULL DEFAULT 0,
    `gender` ENUM('Male', 'Female') NOT NULL,
    `size` ENUM('Small', 'Medium', 'Large', 'Extra Large') NOT NULL DEFAULT 'Medium',
    `color` VARCHAR(60) DEFAULT NULL,
    `description` TEXT NOT NULL,
    `medical_notes` TEXT DEFAULT NULL,
    `vaccinated` BOOLEAN NOT NULL DEFAULT TRUE,
    `spayed_neutered` BOOLEAN NOT NULL DEFAULT TRUE,
    `good_with_kids` BOOLEAN NOT NULL DEFAULT TRUE,
    `good_with_pets` BOOLEAN NOT NULL DEFAULT TRUE,
    `image_url` VARCHAR(500) NOT NULL,
    `status` ENUM('Available', 'Pending', 'Adopted') NOT NULL DEFAULT 'Available',
    `is_approved` BOOLEAN NOT NULL DEFAULT TRUE,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT `fk_pet_shelter` FOREIGN KEY (`shelter_id`) 
        REFERENCES `shelters`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- 5. Table: adoption_requests
-- Applications submitted by adopters for a specific pet
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `adoption_requests` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `pet_id` INT NOT NULL,
    `user_id` INT NOT NULL,
    `housing_type` ENUM('Apartment', 'Independent House', 'Villa / Farmhouse') NOT NULL,
    `has_yard` BOOLEAN NOT NULL DEFAULT FALSE,
    `previous_experience` TEXT NOT NULL,
    `reason_for_adoption` TEXT NOT NULL,
    `contact_phone` VARCHAR(20) NOT NULL,
    `status` ENUM('Pending', 'Approved', 'Rejected', 'Cancelled') NOT NULL DEFAULT 'Pending',
    `shelter_remarks` TEXT DEFAULT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT `fk_request_pet` FOREIGN KEY (`pet_id`) 
        REFERENCES `pets`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_request_user` FOREIGN KEY (`user_id`) 
        REFERENCES `users`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Indexes for performance on dynamic filtering & search
CREATE INDEX `idx_pets_status_approved` ON `pets` (`status`, `is_approved`);
CREATE INDEX `idx_pets_species` ON `pets` (`species`);
CREATE INDEX `idx_shelters_city` ON `shelters` (`city`);
CREATE INDEX `idx_requests_status` ON `adoption_requests` (`status`);

-- ============================================================
-- SAMPLE DATASET
-- Demo accounts use unique, randomized cryptographic hashes.
-- Passwords must be reset or new users registered before login.
-- Hashes generated using werkzeug.security scrypt algorithm.
-- ============================================================

INSERT IGNORE INTO `users` (`id`, `full_name`, `email`, `password_hash`, `phone`, `address`, `role`) VALUES
-- 1. Admin account
(1, 'PawConnect Super Admin', 'admin@pawconnect.org', 'scrypt:32768:8:1$fKuGx8XpAoZA5oCN$e66b282205764c37e51bb20f408116ac4d40e8b7e73a4698f479cce5753ad3ea16568e7109f404cfdf907341418c0b2464a49c2812af5cb01a439cb3910bab59', '+91 98765 00001', 'PawConnect HQ, Innovation Park, Bangalore', 'admin'),

-- 2. Shelter accounts
(2, 'Dr. Aris Thorne (Hope for Paws)', 'hopeforpaws@shelter.org', 'scrypt:32768:8:1$oMf8Xckqe5PKbDHq$6dce9e192f6c96233062d4545154a8010616cedbd0bb59029c881452f194f2698cd08bd4221900e86d3b66a5b74aa482de2ce5274d3b4df81668664655c11232', '+91 98201 11222', '12 Green Meadow Road, Indiranagar, Bangalore', 'shelter'),
(3, 'Meera Sen (Happy Havens Animal Sanctuary)', 'happyhavens@shelter.org', 'scrypt:32768:8:1$2Wu3jAlsry3OBRDW$2930ad7a313d4289fcc219d5b08189fc579e77a826545bf1c0386497d995e1852090afa9f82980f61835e4ab01fd7900d5b0f1ac4a24c02d19208dc564bf1b95', '+91 97112 33445', '78 Sunrise Hills, Bandra West, Mumbai', 'shelter'),
(4, 'Vikram Deshmukh (Green Valley Rescue)', 'greenvalley@shelter.org', 'scrypt:32768:8:1$0ZIrjz1DTAdbw7uv$decdeec32920a81cf5379389cf0d8ec5b325fa3e56795f8d734081cbdc9a91f8473b7f62287e4a33d808fd50925f129c07ca19ea197c082a304d98a750814d8f', '+91 99345 55667', '45 Riverside Enclave, Koregaon Park, Pune', 'shelter'),
(5, 'Sunita Rao (Compassion Pets Care - Pending Verification)', 'newcare@shelter.org', 'scrypt:32768:8:1$tfEbZ0t1rWejSbIR$0417ebb2f55641392efc69ff5e5b3aae532ac8442a10dd82d4f7e843d832c98bc7164e4fb5fba641513ada80762057cf658994aab4ce7f4241a805aa76d72ac6', '+91 98456 77889', '21 Lakeview Circle, Whitefield, Bangalore', 'shelter'),

-- 3. Adopter accounts
(6, 'Pooja Sharma', 'pooja@example.com', 'scrypt:32768:8:1$c201GRFPc3dwoKXC$9121dd5912f90c4c1a53b1bd8e9b89ec86e2ed788247c029c12caf87be777c2bcae82034d684e92861cd2215e1263dcb1191bac022119a19c0150be5f5e5b9cf', '+91 98112 44556', 'Flat 402, Lotus Towers, Koramangala, Bangalore', 'adopter'),
(7, 'Rahul Verma', 'rahul@example.com', 'scrypt:32768:8:1$vdL8ZFZ3GmvS7ixG$60a8df0a38cb8eab34129bcf66429a77124acd2786d1f74791c33faca257a94639196790006c84f81d747faaf8463536c13427a53276e7c8792e872c7bccb7a4', '+91 98223 55667', 'B-10, Sea Breeze Apartments, Juhu, Mumbai', 'adopter'),
(8, 'Ananya Iyer', 'ananya@example.com', 'scrypt:32768:8:1$AxD1oXub78JIY4hI$87aeaff97e06710695656978d26c3ba0b33af180b6c8713aa79504c5584a808e04e5f908da714b15c16bd81cd90282c45e8950e89c8b6dcdc318e8b7f1af919b', '+91 97334 66778', 'Plot 14, Cypress Court, Viman Nagar, Pune', 'adopter');

-- Admin details
INSERT IGNORE INTO `admins` (`id`, `user_id`, `admin_code`, `department`) VALUES
(1, 1, 'ADM-PAW-001', 'Platform Moderation & Safety');

-- Shelters details
INSERT IGNORE INTO `shelters` (`id`, `user_id`, `shelter_name`, `license_number`, `city`, `state`, `address`, `phone`, `email`, `website`, `description`, `is_verified`) VALUES
(1, 2, 'Hope for Paws Rescue Shelter', 'SHELTER-BLR-2021-089', 'Bangalore', 'Karnataka', '12 Green Meadow Road, Indiranagar', '+91 98201 11222', 'hopeforpaws@shelter.org', 'https://hopeforpaws.example.org', 'Dedicated to rescuing, rehabilitating, and rehoming abandoned puppies, dogs, and cats across Karnataka.', TRUE),
(2, 3, 'Happy Havens Sanctuary', 'SHELTER-MUM-2019-304', 'Mumbai', 'Maharashtra', '78 Sunrise Hills, Bandra West', '+91 97112 33445', 'happyhavens@shelter.org', 'https://happyhavens.example.org', 'A warm community sanctuary focused on gentle senior animals, disabled rescues, and finding patient loving adopters.', TRUE),
(3, 4, 'Green Valley Animal Haven', 'SHELTER-PUN-2022-112', 'Pune', 'Maharashtra', '45 Riverside Enclave, Koregaon Park', '+91 99345 55667', 'greenvalley@shelter.org', 'https://greenvalleypets.example.org', 'Fostering companionship between humans and domestic rescues including birds, rabbits, and friendly hounds.', TRUE),
(4, 5, 'Compassion Pets Care', 'SHELTER-BLR-2024-991', 'Bangalore', 'Karnataka', '21 Lakeview Circle, Whitefield', '+91 98456 77889', 'newcare@shelter.org', NULL, 'Newly founded shelter initiative providing emergency animal rescue in suburban Bangalore.', FALSE);

-- Pets dataset with rich details and real pet photos
INSERT IGNORE INTO `pets` (`id`, `shelter_id`, `name`, `species`, `breed`, `age_years`, `age_months`, `gender`, `size`, `color`, `description`, `medical_notes`, `vaccinated`, `spayed_neutered`, `good_with_kids`, `good_with_pets`, `image_url`, `status`, `is_approved`) VALUES
(1, 1, 'Milo', 'Dog', 'Golden Retriever Mix', 2, 4, 'Male', 'Large', 'Golden Cream', 
 'Milo is a gentle, affectionate boy who loves outdoor walks, game fetch sessions, and curling up beside you while you work. He has completed basic obedience training and is wonderful with both kids and other dogs.',
 'Fully vaccinated, microchipped, dewormed. Excellent dental and joint health.', TRUE, TRUE, TRUE, TRUE, 
 'https://images.unsplash.com/photo-1552053831-71594a27632d?auto=format&fit=crop&w=800&q=80', 'Available', TRUE),

(2, 1, 'Luna', 'Cat', 'Calico Domestic Shorthair', 1, 6, 'Female', 'Small', 'Tricolor Calico', 
 'Luna is a curious purr-machine who loves sunbathing on window sills, chasing feather wands, and giving gentle headbutts. She is litter-trained and very clean.',
 'All annual shots up to date. Spayed in March 2024. Healthy appetite.', TRUE, TRUE, TRUE, TRUE, 
 'https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?auto=format&fit=crop&w=800&q=80', 'Available', TRUE),

(3, 2, 'Barnaby', 'Dog', 'Beagle', 3, 2, 'Male', 'Medium', 'Tri-Color Tan & White', 
 'Barnaby is a playful explorer with a sweet, soulful expression and a gentle demeanor. He adores sniff-walks in the park and cuddles on the rug.',
 'Vaccinated against rabies and DHPP. Heartworm negative. Neutered.', TRUE, TRUE, TRUE, TRUE, 
 'https://images.unsplash.com/photo-1537151608828-ea2b11777ee8?auto=format&fit=crop&w=800&q=80', 'Available', TRUE),

(4, 2, 'Bella', 'Dog', 'Labrador Retriever', 1, 1, 'Female', 'Large', 'Rich Chocolate', 
 'Bella is bubbly, bright, and always eager to make new friends. She is house-trained, knows sit, stay, and paw, and would thrive in an active home with a fenced yard or frequent park outings.',
 'Healthy, fully vaccinated, clear veterinary certificate.', TRUE, TRUE, TRUE, TRUE, 
 'https://images.unsplash.com/photo-1587300003388-59208cc962cb?auto=format&fit=crop&w=800&q=80', 'Available', TRUE),

(5, 3, 'Oliver & Chloe', 'Cat', 'British Shorthair Pair', 2, 0, 'Male', 'Medium', 'Silver Tabby & Smoke Gray', 
 'A bonded brother-and-sister duo who bring double the warmth! Oliver is playful and curious, while Chloe loves quiet lap cuddles. We are seeking a loving forever home willing to adopt both together.',
 'Both are spayed/neutered, vaccinated, and indoor-only cats.', TRUE, TRUE, TRUE, TRUE, 
 'https://images.unsplash.com/photo-1573865526739-10659fec78a5?auto=format&fit=crop&w=800&q=80', 'Available', TRUE),

(6, 3, 'Clover', 'Rabbit', 'Holland Lop', 0, 10, 'Female', 'Small', 'Caramel & White', 
 'Clover is a gentle bunny with velvety floppy ears who enjoys munching timothy hay, fresh coriander, and hopping around safe carpeted rooms. She is litter-box trained.',
 'Health check cleared, vaccinated for RHDV.', TRUE, TRUE, TRUE, FALSE, 
 'https://images.unsplash.com/photo-1585110396000-c9ffd4e4b308?auto=format&fit=crop&w=800&q=80', 'Available', TRUE),

(7, 1, 'Rocky', 'Dog', 'Indie Shepherd Mix', 1, 8, 'Male', 'Medium', 'Sandy Fawn', 
 'Rocky was rescued as an orphan pup from a highway junction and nurtured into a healthy, highly intelligent, fiercely loyal companion. He is exceptionally smart, alert, and eager to learn tricks.',
 'Vaccination card complete. Neutered. Very sturdy immunity.', TRUE, TRUE, TRUE, TRUE, 
 'https://images.unsplash.com/photo-1543466835-00a7907e9de1?auto=format&fit=crop&w=800&q=80', 'Available', TRUE),

(8, 2, 'Sunny', 'Bird', 'Cockatiel', 1, 2, 'Male', 'Small', 'Yellow Crested & Gray', 
 'Sunny whistles cheerful melodies in the morning and loves perching on shoulders. He enjoys fresh leafy greens, seeds, and gentle head scratches.',
 'Avian specialist checked, healthy feathers and beak.', TRUE, FALSE, TRUE, FALSE, 
 'https://images.unsplash.com/photo-1552728089-57bdde30beb3?auto=format&fit=crop&w=800&q=80', 'Available', TRUE),

(9, 3, 'Daisy', 'Dog', 'Cocker Spaniel', 4, 0, 'Female', 'Medium', 'Golden Honey', 
 'Daisy has the kindest hazel eyes and a tail that never stops wagging. She is a low-to-medium energy sweetheart who loves peaceful evening strolls and cozy snoozes.',
 'Currently in pending adoption review process with an approved applicant.', TRUE, TRUE, TRUE, TRUE, 
 'https://images.unsplash.com/photo-1518717758536-85ae29035b6d?auto=format&fit=crop&w=800&q=80', 'Pending', TRUE),

(10, 1, 'Simba', 'Cat', 'Ginger Tabby', 2, 5, 'Male', 'Medium', 'Orange Striped', 
 'Simba was successfully matched with a loving family last week! Displayed as an adoption success story.',
 'Healthy, vaccinated, happy in his forever home.', TRUE, TRUE, TRUE, TRUE, 
 'https://images.unsplash.com/photo-1533738363-b7f9aef128ce?auto=format&fit=crop&w=800&q=80', 'Adopted', TRUE),

(11, 4, 'Bruno', 'Dog', 'Boxer Mix', 1, 0, 'Male', 'Large', 'Brindle', 
 'Listing submitted by unverified shelter awaiting admin review.',
 'Healthy puppy shots done.', TRUE, FALSE, TRUE, TRUE, 
 'https://images.unsplash.com/photo-1548199973-03cce0bbc87b?auto=format&fit=crop&w=800&q=80', 'Available', FALSE);

-- Sample Adoption Applications demonstrating various workflow states
INSERT IGNORE INTO `adoption_requests` (`id`, `pet_id`, `user_id`, `housing_type`, `has_yard`, `previous_experience`, `reason_for_adoption`, `contact_phone`, `status`, `shelter_remarks`) VALUES
(1, 9, 6, 'Apartment', FALSE, 'Grew up with a golden retriever for 10 years. Well-versed with feeding, vet schedules, and regular grooming.', 'I work from home and live in a pet-friendly society. Seeking a calm companion to love and care for.', '+91 98112 44556', 'Pending', 'Application under review. Scheduled home visit phone interview.'),
(2, 10, 7, 'Independent House', TRUE, 'Owned 2 rescue cats previously. Experienced in litter training, diet, and feline health.', 'Our family loves animals and we have plenty of open indoor space and cozy corners for a friendly ginger cat.', '+91 98223 55667', 'Approved', 'Home check completed and approved. Adoption finalized successfully!'),
(3, 3, 8, 'Apartment', FALSE, 'First time pet parent, but have spent time volunteering at local animal shelters.', 'I am ready to dedicate time and energy to a beagle. Have done thorough research on breed nutrition and care.', '+91 97334 66778', 'Pending', 'Application received. Pending shelter coordinator review.');
