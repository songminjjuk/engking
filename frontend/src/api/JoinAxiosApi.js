import axios from "axios";

const JoinAxiosApi = {
  // 🍒 이름 중복 확인
  dupNickname: async (name) => {
    try {
      return await axios.post("/member/register", null, {
        params: {
          nickname: name
        }
      });
    } catch (error) {
      throw error;
    }
  },
  // 🍒 이메일 중복 확인
  dupEmail: async (email) => {
    try {
      return await axios.post("/member/register", null, {
        params: {
          email: email
        }
      });
    } catch (error) {
      throw error;
    }
  },
  // 🍒 회원가입
  createUser: async(userData) => {
    try {
      return await axios.post("/member/register", userData, {
      })
    } catch(error) {
      throw error;
    }
  },
  // 🍒 Authkey 인증
//   confirmAuthKey: async (email, authKey) => {
//     try {
//       return await axios.post("/join/auth", null, {
//         params: {
//           email: email,
//           authKey: authKey
//         }
//       });
//     } catch (error) {
//       throw error;
//     }
//   },
};

export default JoinAxiosApi;
