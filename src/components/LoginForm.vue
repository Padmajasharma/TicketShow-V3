<template>
  <div class="auth-container">
    <div class="auth-card">
      <div class="header-section">
        <h1 class="auth-title">Sign In</h1>
        <p class="auth-subtitle">Welcome back</p>
      </div>

      <div v-if="message" class="alert" :class="message.includes('success') ? 'alert-success' : 'alert-error'">
        {{ message }}
      </div>

      <form @submit.prevent="login" class="auth-form">
        <div class="form-group">
          <label for="username">Username</label>
          <input id="username" type="text" v-model="username" placeholder="Your username" required />
        </div>

        <div class="form-group">
          <label for="password">Password</label>
          <input id="password" type="password" v-model="password" placeholder="Your password" required />
        </div>

        <button type="submit" class="btn-submit">Sign In</button>
      </form>

      <div style="text-align:center; margin-top:8px;">
        <button class="btn-secondary" @click="showOtpPanel = !showOtpPanel">Sign in with OTP</button>
      </div>

      <div v-if="showOtpPanel" class="otp-panel" style="margin-top:12px;">
        <div class="form-group">
          <label for="otpIdentifier">Email or Phone</label>
          <input id="otpIdentifier" type="text" v-model="otpIdentifier" placeholder="email or +911234..." />
        </div>

        <div style="display:flex; gap:8px; margin-top:8px; align-items:center;">
          <button class="btn-primary" @click="sendOtpEmail">Send OTP</button>
          <input v-model="otpCode" placeholder="6-digit code" style="flex:1;padding:12px;border-radius:8px;border:1px solid #e5e7eb;" />
          <button class="btn-primary" @click="verifyOtpLogin">Verify</button>
        </div>
        <p v-if="otpMessage" :class="{ 'alert-error': otpError, 'alert-success': !otpError }" style="margin-top:8px">{{ otpMessage }}</p>
      </div>

      <p class="auth-footer">
        Don't have an account? 
        <router-link to="/signup" class="link">Create one</router-link>
      </p>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { setupTokenExpirationTimer } from '../main';

export default {
  data() {
    return {
      username: '',
      password: '',
      message: '', 
      // OTP UI state
      showOtpPanel: false,
      otpIdentifier: '',
      otpCode: '',
      otpMessage: '',
      otpError: false,
    };
  },
  methods: {
    login() {
      const headers = { 'Content-Type': 'application/json'};
    
      axios.post('login', {
        username: this.username,
        password: this.password,
      },{headers})
      .then(response => {
        
        const token = response.data.token;
        const is_admin = response.data.is_admin;
       
        localStorage.setItem('access_token', token);
        
        localStorage.setItem('is_admin', is_admin);
        
        // Set up token expiration timer after successful login
        setupTokenExpirationTimer(this.$router);
        
        // Check for redirect query parameter
        const redirect = this.$route.query.redirect;
        if (redirect) {
          this.$router.push(redirect);
        } else if (is_admin) {
          this.$router.push('/admindashboard');
        } else {
          this.$router.push('/userdashboard');
        }
      })
      .catch(error => {
        if (error.response && error.response.data && error.response.data.message) {
          this.message = error.response.data.message;
        } else {
          this.message = 'An error occurred during login';
        }
      });
    },
    async sendOtpEmail() {
      this.otpMessage = '';
      this.otpError = false;
      const identifier = this.otpIdentifier || this.username;
      if (!identifier) {
        this.otpMessage = 'Please enter email or phone to send OTP';
        this.otpError = true;
        return;
      }
      try {
        const resp = await window.axios.post('/auth/send-otp', { identifier, via: 'email' });
        this.otpMessage = resp.data?.message || 'OTP sent';
        this.otpError = false;
      } catch (e) {
        this.otpError = true;
        this.otpMessage = e.response?.data?.message || e.message || 'Failed to send OTP';
        console.error('sendOtpEmail error', e);
      }
    },
    async verifyOtpLogin() {
      this.otpMessage = '';
      this.otpError = false;
      const identifier = this.otpIdentifier || this.username;
      if (!identifier || !this.otpCode) {
        this.otpMessage = 'Please provide identifier and code';
        this.otpError = true;
        return;
      }
      try {
        const resp = await window.axios.post('/auth/verify-otp', { identifier, code: this.otpCode });
        this.otpMessage = resp.data?.message || 'Verified';
        const token = resp.data?.token;
        if (token) {
          localStorage.setItem('access_token', token);
          setupTokenExpirationTimer(this.$router);
          this.$router.push('/userdashboard');
        }
      } catch (e) {
        this.otpError = true;
        this.otpMessage = e.response?.data?.message || e.message || 'OTP verify failed';
        console.error('verifyOtpLogin error', e);
      }
    }
  },
};
</script>

<style scoped>
* {
  box-sizing: border-box;
}

.auth-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background:
    radial-gradient(circle at 0% 0%, rgba(217, 212, 241, 0.9) 0, transparent 55%),
    radial-gradient(circle at 100% 0%, rgba(250, 220, 217, 0.9) 0, transparent 55%),
    radial-gradient(circle at 0% 100%, rgba(215, 234, 248, 0.9) 0, transparent 55%),
    #f9fafb;
}

.auth-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 24px;
  padding: 48px;
  width: 100%;
  max-width: 440px;
  box-shadow: 0 8px 32px rgba(168, 85, 247, 0.08);
  border: 1px solid rgba(168, 85, 247, 0.1);
  animation: slideInUp 0.5s ease-out;
}

.header-section {
  text-align: center;
  margin-bottom: 32px;
}

.auth-title {
  font-size: 28px;
  background: linear-gradient(135deg, #a855f7 0%, #ec4899 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 8px 0;
  font-weight: 700;
  letter-spacing: -0.5px;
}

.auth-subtitle {
  font-size: 15px;
  color: #6b7280;
  margin: 0;
  font-weight: 400;
}

.alert {
  padding: 14px 18px;
  border-radius: 16px;
  margin-bottom: 24px;
  font-size: 14px;
  animation: fadeIn 0.3s ease-out;
  text-align: center;
}

.alert-success {
  background-color: #d4f4dd;
  color: #2f855a;
}

.alert-error {
  background-color: #fed7d7;
  color: #c53030;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
  margin-bottom: 28px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 13px;
  color: #718096;
  font-weight: 500;
  letter-spacing: 0.2px;
  text-transform: uppercase;
}

.form-group input {
  padding: 14px 18px;
  border: 2px solid #f0e7ef;
  border-radius: 16px;
  font-size: 15px;
  color: #2d3748;
  transition: all 0.3s ease;
  background-color: #fafafa;
  font-family: inherit;
}

.form-group input::placeholder {
  color: #cbd5e0;
}

.form-group input:focus {
  outline: none;
  border-color: #a855f7;
  background-color: #ffffff;
  box-shadow: 0 0 0 3px rgba(168, 85, 247, 0.1);
}

.btn-submit {
  width: 100%;
  padding: 16px;
  background: linear-gradient(135deg, #a855f7 0%, #ec4899 100%);
  color: #ffffff;
  border: none;
  border-radius: 16px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 8px;
  letter-spacing: 0.3px;
  box-shadow: 0 4px 15px rgba(168, 85, 247, 0.3);
}

.btn-submit:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(168, 85, 247, 0.4);
}

.btn-submit:active {
  transform: translateY(0);
}

.auth-footer {
  text-align: center;
  font-size: 14px;
  color: #a0aec0;
  margin: 0;
}

.link {
  color: #a855f7;
  text-decoration: none;
  font-weight: 600;
  transition: color 0.3s ease;
}

.link:hover {
  color: #ec4899;
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@media (max-width: 480px) {
  .auth-card {
    padding: 36px 28px;
  }

  .auth-title {
    font-size: 24px;
  }

  .form-group input {
    padding: 12px 16px;
  }

  .btn-submit {
    padding: 14px;
  }
}
</style>