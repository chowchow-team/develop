import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import {MainForm, NavForm, DetailForm, CreateForm} from './main';
import { SignupForm, LoginForm, LogoutForm, FindIDForm, FindPWForm, ResetPWForm, SettingForm, SignupRedirect } from './account';
import { ProfileForm, ProfileDetailForm, UserFollowListForm } from './profile';
import { AnimalDMForm } from './chat';
import { FriendListForm } from './friend';
import { NotFoundForm, FooterForm} from './snippets';

import { UserProvider } from './UserContext';

function App() {
  return (
    <UserProvider>
        <Router>
            <div className="App">
                <NavForm />
                <Routes>
                    <Route path="/" element={<MainForm />} />
                    <Route path="/signup" element={<SignupForm />} />
                    <Route path="/login" element={<LoginForm />} />
                    <Route path="/logout" element={<LogoutForm />} />
                    <Route path="/profile/edit" element={<ProfileForm />} />
                    <Route path="/profile/:username" element={<ProfileDetailForm />} />
                    <Route path="/profile/followlist/:username/:flag" element={<UserFollowListForm />} />
                    <Route path="/friend" element={<FriendListForm />} />
                    <Route path="/animal-dm/:username" element={<AnimalDMForm />} />
                    <Route path="/find-id" element={<FindIDForm />} />
                    <Route path="/find-pw" element={<FindPWForm />} />
                    <Route path="/password-reset/:uidb64/:token" element={<ResetPWForm />} />
                    <Route path="/password-change" element={<ResetPWForm />} />
                    <Route path="/setting" element={<SettingForm />} />
                    <Route path="/activate/:uidb64/:token" element={<SignupRedirect />} />
                    <Route path="/feed/posts/:pk" element={<DetailForm />} />
                    <Route path="/feed/posts/create" element={<CreateForm />} />
                    <Route path="/admin" element={<MainForm />} />
                    <Route path="*" element={<NotFoundForm />} />
                </Routes>
                <FooterForm />
            </div>
        </Router>
    </UserProvider>
  );
}

export default App;
