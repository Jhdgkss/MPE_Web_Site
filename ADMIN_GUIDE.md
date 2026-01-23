# Admin Panel Guide - Site Configuration

## 🎯 Overview

You can now edit your website's hero section, logo, and contact information directly from the Django admin panel!

## 🚀 How to Access

1. **Go to the admin panel**: http://127.0.0.1:8000/admin/
2. **Login** with your admin credentials
3. Look for **"Site Configuration"** in the Core section

## ✏️ What You Can Edit

### 📷 Logo & Branding
- **Logo**: Upload your company logo (PNG with transparent background recommended)
  - Used in header navigation and footer
  - Replaces the current MPE logo throughout the site

### 🎨 Hero Section (Homepage Showcase)

**Hero Title** (e.g., "MPE i6")
- Large white heading at top of hero section
- Maximum 100 characters

**Hero Subtitle** (e.g., "Inline tray Sealer")
- Light blue subtitle below title
- Maximum 150 characters

**Hero Description**
- Gray descriptive text below subtitle
- Full paragraph explaining the product

**Hero Image**
- Large showcase machine image on the right side
- Upload high-quality product photos
- Current default: i6.png

**Hero Button Text** (e.g., "VIEW MACHINES")
- Text displayed on the blue button
- Maximum 50 characters

**Hero Button Link** (e.g., "#machines" or "/shop/")
- Where the button links to
- Use `#machines` to scroll to machines section
- Or use `/shop/` for another page

### ⭐ Feature Bullets
Three key features shown below the hero button:
- **Feature 1** (default: "UK manufacturing")
- **Feature 2** (default: "Service support")
- **Feature 3** (default: "Custom automation")

### 📞 Contact Information
Used in header, footer, and contact page:
- **Phone Number** (e.g., "+44 1663 732700")
- **Email** (e.g., "sales@mpe-uk.com")
- **Location** (e.g., "Derbyshire, UK")

### 📱 Social Media
Links shown in top bar:
- **LinkedIn URL** (full URL to your LinkedIn profile)
- **Facebook URL** (full URL to your Facebook page)
- **YouTube URL** (full URL to your YouTube channel)

## 📝 Step-by-Step: Editing the Hero Section

1. **Access Admin**: Go to http://127.0.0.1:8000/admin/
2. **Find Site Configuration**: Click on "Site Configuration" under "Core"
3. **Click the entry**: You'll see one configuration record
4. **Edit fields**: 
   - Change "MPE i6" to your product name
   - Update the subtitle
   - Modify the description
   - Upload a new hero image (click "Choose File")
   - Customize button text and link
5. **Save**: Click "SAVE" at the bottom
6. **View changes**: Go to http://127.0.0.1:8000/ to see your updates!

## 🖼️ Uploading Images

### Logo Image
- **Recommended format**: PNG with transparent background
- **Recommended size**: 150-200px height
- **Best practices**: 
  - Use white or light-colored logo for dark theme
  - Keep it simple and recognizable
  - Test how it looks in both header and footer

### Hero/Showcase Image
- **Recommended format**: PNG or JPG
- **Recommended size**: 1200px wide or larger
- **Best practices**:
  - Use high-quality product photography
  - Show machine from best angle
  - Clean background or transparent PNG
  - Professional lighting

## 🔒 Security Notes

- **Only one configuration**: The system prevents creating multiple configurations
- **Cannot delete**: The configuration cannot be deleted (only edited)
- **Requires admin access**: Only staff users can access the admin panel

## 💡 Tips & Tricks

### Hero Section Best Practices
1. **Title**: Keep it short and memorable (product name or model number)
2. **Subtitle**: Describe the product type (e.g., "Inline tray Sealer")
3. **Description**: Focus on key benefits (speed, efficiency, features)
4. **Image**: Use your best product photo - this is the first thing visitors see!

### Feature Bullets
- Keep them short (2-3 words)
- Focus on unique selling points
- Use action-oriented language

### Contact Info
- Always keep phone and email current
- Use international format for phone (+44...)
- Test all social media links after adding them

## 🎯 Common Tasks

### Change the Hero Machine
1. Admin → Site Configuration
2. Find "Hero image" field
3. Click "Choose File"
4. Upload new machine photo
5. Save
6. Refresh website to see changes

### Update Company Logo
1. Admin → Site Configuration
2. Find "Logo" field
3. Click "Choose File"
4. Upload new logo (PNG recommended)
5. Save
6. Logo updates in header and footer automatically

### Modify Hero Text
1. Admin → Site Configuration
2. Edit "Hero title", "Hero subtitle", and "Hero description"
3. Save
4. Changes appear immediately on homepage

## 🔄 Changes Take Effect Immediately

All changes in the admin panel are **live immediately**:
- No need to restart the server
- Just save and refresh your browser
- You may need to hard refresh (Ctrl+Shift+R) if images don't update

## 📋 Checklist for New Setup

- [ ] Upload company logo
- [ ] Add hero showcase image
- [ ] Customize hero title and subtitle
- [ ] Update hero description
- [ ] Set feature bullets
- [ ] Verify contact information
- [ ] Add social media URLs
- [ ] Test all changes on live site
- [ ] Check mobile responsiveness

## 🆘 Troubleshooting

**Images not showing?**
- Check file size (keep under 5MB)
- Verify file format (JPG, PNG)
- Try hard refresh (Ctrl+Shift+R)
- Check file uploaded successfully in admin

**Changes not appearing?**
- Did you click "SAVE"?
- Try hard refresh (Ctrl+Shift+R)
- Clear browser cache
- Check you're viewing the right page

**Can't access admin?**
- Verify you're using correct URL: /admin/
- Check your login credentials
- Ensure your account has staff/admin status

## 🎨 Example Configuration

```
Hero Title: MPE i6
Hero Subtitle: Inline tray Sealer
Hero Description: High-speed inline tray sealer. Electric operation for maximum produce.
Hero Button Text: VIEW MACHINES
Hero Button Link: #machines

Feature 1: UK manufacturing
Feature 2: Service support  
Feature 3: Custom automation

Phone: +44 1663 732700
Email: sales@mpe-uk.com
Location: Derbyshire, UK
```

---

**Need help?** All settings are clearly labeled in the admin panel with helpful descriptions!
