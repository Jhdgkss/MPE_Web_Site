Password Reset + Admin User Email (Patch)

What this adds
- Customer portal "Forgot your password?" link.
- Standard Django password reset flow:
  /customer/password-reset/
  /customer/password-reset/done/
  /customer/reset/<uidb64>/<token>/
  /customer/reset/done/
- Styled reset templates under templates/registration/.
- Admin: User list shows username + email, and email is required when creating new users in /admin/.

Notes
- This does NOT allow public signup. Accounts are still created by admins only.
- You cannot (and should not) view existing passwords in plaintext. Django stores hashed passwords.
  Admins can reset a user password from /admin/ safely.

After applying
1) Ensure EMAIL settings are correct (Brevo/SMTP etc) so reset emails can send.
2) Test:
   - Go to /customer/login/ -> click "Forgot your password?"
   - Enter a user email -> confirm the email arrives and the link works.
