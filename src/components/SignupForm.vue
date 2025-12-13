<template>
  <div class="auth-container">
    <div class="auth-card">
      <div class="header-section">
        <h1 class="auth-title">Create Account</h1>
        <p class="auth-subtitle">Join us today</p>
      </div>

      <div v-if="message" class="alert" :class="message.includes('success') ? 'alert-success' : 'alert-error'">
        {{ message }}
      </div>

      <form @submit.prevent="signup" class="auth-form">
        <div class="form-group">
          <label for="email">Email</label>
          <input id="email" type="email" v-model="email" placeholder="your@email.com" required />
        </div>

        <div class="form-group">
          <label for="username">Username</label>
          <input id="username" type="text" v-model="username" placeholder="Choose a username" required />
        </div>

        <div class="form-group">
          <label for="password">Password</label>
          <input id="password" type="password" v-model="password" placeholder="Create a password" required />
        </div>

        <button type="submit" class="btn-submit">Create Account</button>
      </form>

        <div style="text-align:center; margin-top:8px;">
          <button class="btn-secondary" @click="showOtpPanel = !showOtpPanel">Or verify via Email OTP</button>
        </div>

        <div v-if="showOtpPanel" style="margin-top:12px;">
          <div class="form-group">
            <label>Email</label>
            <input type="email" v-model="email" placeholder="your@email.com" />
          </div>
          <div style="display:flex; gap:8px; margin-top:8px; align-items:center;">
            <button class="btn-primary" @click="sendOtpSignup">Send OTP</button>
            <input v-model="otpCode" placeholder="6-digit code" style="flex:1;padding:12px;border-radius:8px;border:1px solid #e5e7eb;" />
            <button class="btn-primary" @click="verifyOtpSignup">Verify</button>
          </div>
          <p v-if="otpMessage" :class="{ 'alert-error': otpError, 'alert-success': !otpError }" style="margin-top:8px">{{ otpMessage }}</p>
        </div>

        <p class="auth-footer">
          Already have an account? 
          <router-link to="/login" class="link">Sign in</router-link>
        </p>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      email: '',
      username: '',
      password: '',
      message: '',
      // OTP helper UI
      showOtpPanel: false,
      otpCode: '',
      otpMessage: '',
      otpError: false,
    };
  },
  methods: {
    signup() {
      
      const headers = { 'Content-Type': 'application/json'};

      axios.post('signup', {
        email: this.email,
        username: this.username,
        password: this.password
      })
        .then(response => {
         
          this.message = response.data.message; 
          this.$router.push('/login'); 
        })
        .catch(error => {
          if (error.response && error.response.data) {
            // Check for 'message', 'error', or 'msg' fields from backend
            this.message = error.response.data.message || error.response.data.error || error.response.data.msg || 'An error occurred during signup';
          } else {
            this.message = 'An error occurred during signup';
          }
        });
    }
    ,
    async sendOtpSignup() {
      this.otpMessage = '';
      this.otpError = false;
      if (!this.email) {
        this.otpMessage = 'Please enter your email to receive OTP';
        this.otpError = true;
        return;
      }
      try {
        const resp = await window.axios.post('/auth/send-otp', { identifier: this.email, via: 'email' });
        this.otpMessage = resp.data?.message || 'OTP sent';
        this.otpError = false;
      } catch (e) {
        this.otpError = true;
        this.otpMessage = e.response?.data?.message || e.message || 'Failed to send OTP';
        console.error('sendOtpSignup error', e);
      }
    },
    async verifyOtpSignup() {
      this.otpMessage = '';
      this.otpError = false;
      if (!this.email || !this.otpCode) {
        this.otpMessage = 'Please provide email and code';
        this.otpError = true;
        return;
      }
      try {
        const resp = await window.axios.post('/auth/verify-otp', { identifier: this.email, code: this.otpCode });
        this.otpMessage = resp.data?.message || 'Verified';
        const token = resp.data?.token;
        if (token) {
          localStorage.setItem('access_token', token);
          this.$router.push('/userdashboard');
        }
      } catch (e) {
        this.otpError = true;
        this.otpMessage = e.response?.data?.message || e.message || 'OTP verify failed';
        console.error('verifyOtpSignup error', e);
      }
    }
  }
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