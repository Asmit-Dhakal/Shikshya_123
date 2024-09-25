const API_URL = 'http://localhost:8000'; // Your API endpoint
let TOKEN = '';  // This will hold the JWT token after login

// 1. Load Courses for the Teacher
async function loadCourses() {
    const response = await fetch(`${API_URL}/courses/`, {
        headers: {
            'Authorization': `Bearer ${TOKEN}`
        }
    });
    const courses = await response.json();
    displayCourses(courses);
}

function displayCourses(courses) {
    const coursesList = document.getElementById('courses-list');
    coursesList.innerHTML = '';  // Clear the list first
    courses.forEach(course => {
        const courseItem = document.createElement('div');
        courseItem.innerHTML = `
            <h3>${course.title}</h3>
            <p>${course.description}</p>
            <p>Price: $${course.price}</p>
            <button onclick="editCourse(${course.id})">Edit</button>
            <button onclick="deleteCourse(${course.id})">Delete</button>
        `;
        coursesList.appendChild(courseItem);

        // Add to the course-select dropdown for chapter/video management
        const courseOption = document.createElement('option');
        courseOption.value = course.id;
        courseOption.textContent = course.title;
        document.getElementById('course-select').appendChild(courseOption);
    });
}

// 2. Create a New Course
document.getElementById('course-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('title', document.getElementById('title').value);
    formData.append('description', document.getElementById('description').value);
    formData.append('price', document.getElementById('price').value);
    formData.append('validation_date', document.getElementById('validation_date').value);
    formData.append('thumbnail', document.getElementById('thumbnail').files[0]);  // Thumbnail file

    const response = await fetch(`${API_URL}/courses/create/`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${TOKEN}`
        },
        body: formData
    });

    if (response.ok) {
        alert('Course created successfully!');
        loadCourses();
    } else {
        alert('Failed to create course');
    }
});

// 3. Upload Video for a Chapter
document.getElementById('video-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const courseId = document.getElementById('course-select').value;
    const chapterTitle = document.getElementById('chapter-title').value;
    const videoTitle = document.getElementById('video-title').value;
    const videoFile = document.getElementById('video-file').files[0];

    const formData = new FormData();
    formData.append('title', videoTitle);
    formData.append('chapter_title', chapterTitle);
    formData.append('video_file', videoFile);

    const response = await fetch(`${API_URL}/chapters/${courseId}/videos/create/`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${TOKEN}`
        },
        body: formData
    });

    if (response.ok) {
        alert('Video uploaded successfully!');
    } else {
        alert('Failed to upload video');
    }
});

// 4. Load Enrollments for Teacher
async function loadEnrollments() {
    const response = await fetch(`${API_URL}/courses/booked/`, {
        headers: {
            'Authorization': `Bearer ${TOKEN}`
        }
    });
    const enrollments = await response.json();
    displayEnrollments(enrollments);
}

function displayEnrollments(enrollments) {
    const enrollmentsList = document.getElementById('enrollments-list');
    enrollmentsList.innerHTML = '';  // Clear the list first
    enrollments.forEach(enrollment => {
        const enrollmentItem = document.createElement('div');
        enrollmentItem.innerHTML = `
            <p>Student: ${enrollment.student}</p>
            <p>Course: ${enrollment.course}</p>
            <p>Payment Status: ${enrollment.payment_info.status}</p>
        `;
        enrollmentsList.appendChild(enrollmentItem);
    });
}

// Initialize by loading courses and enrollments on page load
loadCourses();
loadEnrollments();
