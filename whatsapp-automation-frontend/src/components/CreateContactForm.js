import React, { useState } from 'react';
import { createContact } from '../api';

const CreateContactForm = () => {
    const [formData, setFormData] = useState({
        full_name: '',
        phone: '',
        email: '',
    });

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData({ ...formData, [name]: value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await createContact(formData);
            alert('Contact created successfully!');
        } catch (error) {
            console.error('Error creating contact:', error);
            alert('Failed to create contact.');
        }
    };

    return (
        <form onSubmit={handleSubmit}>
            <div>
                <label>Full Name:</label>
                <input
                    type="text"
                    name="full_name"
                    value={formData.full_name}
                    onChange={handleChange}
                    required
                />
            </div>
            <div>
                <label>Phone:</label>
                <input
                    type="text"
                    name="phone"
                    value={formData.phone}
                    onChange={handleChange}
                    required
                />
            </div>
            <div>
                <label>Email:</label>
                <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    required
                />
            </div>
            <button type="submit">Create Contact</button>
        </form>
    );
};

export default CreateContactForm;