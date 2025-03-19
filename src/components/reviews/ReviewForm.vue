<template>
  <div class="review-form">
    <v-form ref="form" @submit.prevent="submitReview">
      <div class="text-center mb-4">
        <h3 class="text-h6">Rate your experience</h3>
        <v-rating
          v-model="rating"
          color="amber"
          hover
          length="5"
          size="40"
          :rules="[v => !!v || 'Please provide a rating']"
          required
        ></v-rating>
      </div>
      
      <v-textarea
        v-model="comment"
        label="Leave your feedback (optional)"
        counter="500"
        rows="4"
        outlined
        :rules="commentRules"
      ></v-textarea>
      
      <v-btn
        type="submit"
        color="primary"
        block
        :loading="loading"
      >
        Submit Review
      </v-btn>
    </v-form>
  </div>
</template>

<script>
export default {
  name: 'ReviewForm',
  props: {
    loading: {
      type: Boolean,
      default: false
    },
    initialRating: {
      type: Number,
      default: 0
    },
    initialComment: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      rating: this.initialRating || 5,
      comment: this.initialComment || '',
      commentRules: [
        v => !v || v.length <= 500 || 'Comment must be less than 500 characters'
      ]
    }
  },
  methods: {
    submitReview() {
      if (this.$refs.form.validate()) {
        this.$emit('submit', {
          rating: this.rating,
          comment: this.comment
        });
      }
    },
    reset() {
      this.rating = 5;
      this.comment = '';
      if (this.$refs.form) {
        this.$refs.form.resetValidation();
      }
    }
  },
  watch: {
    initialRating(newVal) {
      this.rating = newVal;
    },
    initialComment(newVal) {
      this.comment = newVal;
    }
  }
}
</script>

<style scoped>
.review-form {
  padding: 20px 0;
}
</style>
