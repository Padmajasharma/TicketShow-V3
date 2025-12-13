<template>
  <div class="otp-test container card">
    <h2>OTP Tester (Dev)</h2>

    <div class="field">
      <label>Identifier (email or phone)</label>
      <input v-model="identifier" placeholder="user@example.com or +911234567890" />
    </div>

    <div class="field">
      <label>Send via</label>
      <select v-model="via">
        <option value="email">Email</option>
        <option value="sms">SMS</option>
      </select>
    </div>

    <div style="display:flex; gap:8px; margin-top:8px;">
      <button class="btn-primary" @click="sendOtp">Send OTP</button>
      <button class="btn-secondary" @click="clear">Clear</button>
    </div>

    <p v-if="sendMessage" :class="{'text-muted': !sendError, 'text-accent': sendError}">{{ sendMessage }}</p>

    <hr />

    <div class="field">
      <label>Code</label>
      <input v-model="code" placeholder="Enter 6-digit code" />
    </div>

    <div style="display:flex; gap:8px; margin-top:8px;">
      <button class="btn-primary" @click="verifyOtp">Verify OTP</button>
      <button class="btn-secondary" @click="useToken">Save Token Locally</button>
    </div>

    <p v-if="verifyMessage" :class="{'text-muted': !verifyError, 'text-accent': verifyError}">{{ verifyMessage }}</p>

    <div v-if="token" style="margin-top:12px;">
      <p><strong>Token:</strong></p>
      <textarea style="width:100%;height:80px">{{ token }}</textarea>
      <p style="margin-top:8px">You can click "Save Token Locally" to store it as `access_token` in localStorage.</p>
    </div>

  </div>
</template>

<script>
export default {
  name: 'OtpTest',
  data() {
    return {
      identifier: '',
      via: 'email',
      code: '',
      sendMessage: '',
      sendError: false,
      verifyMessage: '',
      verifyError: false,
      token: ''
    };
  },
  methods: {
    async sendOtp() {
      this.sendMessage = '';
      this.sendError = false;
      if (!this.identifier) {
        this.sendMessage = 'Please enter an identifier';
        this.sendError = true;
        return;
      }
      try {
        const resp = await window.axios.post(`/auth/send-otp`, { identifier: this.identifier, via: this.via });
        this.sendMessage = resp.data?.message || 'OTP request sent';
        this.sendError = false;
      } catch (e) {
        this.sendError = true;
        this.sendMessage = e.response?.data?.message || (e.message || 'Send OTP failed');
        console.error('Send OTP error', e);
      }
    },
    async verifyOtp() {
      this.verifyMessage = '';
      this.verifyError = false;
      if (!this.identifier || !this.code) {
        this.verifyMessage = 'Please provide identifier and code';
        this.verifyError = true;
        return;
      }
      try {
        const resp = await window.axios.post(`/auth/verify-otp`, { identifier: this.identifier, code: this.code });
        this.verifyMessage = resp.data?.message || 'Verified';
        this.token = resp.data?.token || '';
        this.verifyError = false;
      } catch (e) {
        this.verifyError = true;
        this.verifyMessage = e.response?.data?.message || (e.message || 'Verify OTP failed');
        console.error('Verify OTP error', e);
      }
    },
    useToken() {
      if (this.token) {
        localStorage.setItem('access_token', this.token);
        this.verifyMessage = 'Token saved to localStorage as access_token';
        this.verifyError = false;
      } else {
        this.verifyMessage = 'No token to save';
        this.verifyError = true;
      }
    },
    clear() {
      this.identifier = '';
      this.code = '';
      this.sendMessage = '';
      this.verifyMessage = '';
      this.token = '';
    }
  }
};
</script>

<style scoped>
.otp-test { padding: 18px; margin-top: 20px; }
.field { margin-top: 10px; display:flex; flex-direction:column; gap:6px; }
input, textarea, select { padding: 10px; border-radius: 8px; border: 1px solid #e5e7eb; }
.btn-primary { background: #a855f7; color: #fff; padding: 10px 14px; border-radius: 8px; border: none; }
.btn-secondary { background: #fff; color: #6b7280; padding: 10px 14px; border-radius: 8px; border: 1px solid #e5e7eb; }
.text-muted { color: #065f46; }
.text-accent { color: #b91c1c; }
</style>
