# 🐾 The Nutri Cat

**Personal Nutrition Assistant Web App — Built with Flask, PostgreSQL, AWS & AI Tools**

---

## 🧠 Project Overview

**The Nutri Cat** is a full-stack nutrition recipe manager that began with an unconventional challenge: transforming a set of encrypted PDF files — containing specialized nutritionist-designed meal plans — into a user-friendly digital experience. Traditional text extraction tools failed to process these PDFs. As a result, I developed a custom pipeline combining **image recognition and OCR (Optical Character Recognition)** techniques to extract the text content from the documents.

To visually enhance the platform, I integrated the **DeepAI API** to generate custom recipe images based on the data extracted from each recipe — making every dish visually appealing even without source media.

This project was developed as my **final submission for Harvard's CS50x course** and stands as a showcase of my web development skills, backend logic, cloud integration, and real-world problem-solving.

---

## 🚀 Live Features

### 🍽️ Core Recipes Page
- Search recipes by **title**, **tags**, and **ingredients**
- Filter and sort by **meal type**, **day of the week**, or **menu name**
- Paginated recipe cards with:
  - Title
  - Tags
  - Generated image
  - Quick link to details
  - Add to favorites button

### ✏️ Recipe Management
- **Create**, **edit**, or **delete** your own recipes
- Add and manage **notes** for each recipe
- Adjust **servings** dynamically
- Mark recipes as **favorites** and view them in a dedicated page

### 🧾 Menu Planning
- View curated weekly **menus created by a certified nutritionist**
- Menus organized by **day of the week** and **meal type** (breakfast, lunch, dinner, dessert)
- See a visual breakdown of recipe titles and links per day
- **Shopping list** generation (currently copies ingredients for the whole week)

### 🔎 Global Search Modal
- Accessible from any page
- Live recipe search (AJAX) by title with matching results and preview images
- **Clickable menu categories** with image thumbnails to explore menus directly

### 👤 User Profile
- View personal account data
- Change **username** or **password**
- **Secure logout**

### 🛡️ Authentication System
- User **registration** and **login**
- **Password reset** via secure email tokens
- Integrated **Google reCAPTCHA** to prevent bot signups

---

## 🧱 Technologies Used

### 🔧 Backend
- **Flask** (Python web framework)
- **SQLAlchemy** (ORM)
- **PostgreSQL** via **Amazon RDS**

### 🗃️ Frontend
- **HTML/CSS/JavaScript**
- Live search & form validation via **vanilla JavaScript**

### ☁️ Cloud & DevOps
- **Amazon S3** for image file storage
- **Amazon RDS** for PostgreSQL database hosting
- Project will be prepared for container-based deployment

### 🤖 Additional Tools Integration
- **Tesseract OCR** for PDF text extraction via image recognition
- **DeepAI API** for custom image generation from recipe data

---

## 💡 Key Accomplishments

- Transformed inconvenient encrypted PDFs into a modern, browsable recipe web app.
- Implemented advanced filtering and search features for recipes.
- Designed a robust, secure user system with password reset and spam prevention.
- Integrated custom image generation via an AI API for a visually rich user experience.
- Built scalable cloud infrastructure using AWS for real-world deployment readiness.

---

## 📸 Demo Screenshots

> *(Optional — include screenshots or a short walkthrough video link here)*

---

## 📬 Contact

If you're a recruiter, instructor, or fellow developer and would like to know more about the project or my work, feel free to reach out:

- **Name**: Kseniia
- **GitHub**: [github.com/UnicornDevCraft](https://github.com/UnicornDevCraft)
- **LinkedIn**: [linkedin.com/in/kseniia-usyk](https://linkedin.com/in/kseniia-usyk)
- **Email**: kseniia.usyk@outlook.com

---

## ✅ Final Submission

This project was submitted as the final assignment for **[CS50x 2025](https://cs50.harvard.edu/x/2025/)** and represents my technical depth, project design, and drive to turn real-life constraints into engaging software solutions.

---