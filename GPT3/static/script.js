
         var app = new Vue({
             el: '#kanbanapp',
             data: {
                 name: '',
                 subject: '',
                 email_prompt: '',
                 task_type: '',
                 tasks: ["blank"],
                 emails: ["blank"],
                 new_id: '',
                 new_name: '',
                 new_content: '',
                 new_deadline: '',
                 new_completed_flag: '',
                 new_list_id: '',

                 job_title: '',
                 job_responsibilities: '',
                 job_requirements: '',
                 lists: ["blank"],
                 jobdescs: ["blank"],
                 new_list_list_id: '',
                 new_list_title: '',

                 task: '',
                 list_holding_these_tasks: '',
                 what_to_do: '',
                 list_name_for_deletion: '',
                 //id: '',
                 list_list_id: '',
                 current_list_id: '',
                 list: '',
                 username: 'blank',

             },
             delimiters: ['{','}'],

             methods: {
                 showModal(id) {
                     this.$refs[id].show()
                 },
                 hideModal(id) {
                     this.$refs[id].hide()
                 },

                 email_addition_button(){
                         axios.post("http://127.0.0.1:5000/insert_email/"+this.username,
                             {name : this.name, subject : this.subject, email_prompt : this.email_prompt}
                         )
                         .then(res => {
                             console.log(res)
                             alert('New task added 🫡')
                             this.name = ''
                             this.subject = ''
                             this.email_prompt = ''

                             app.hideModal('email-creation')
                             app.getTasks()
                         })
                 },

                 jobdesc_addition_button(){
                         axios.post("http://127.0.0.1:5000/insert_jobdesc/"+this.username,
                             {job_title : this.job_title, job_responsibilities : this.job_responsibilities, job_requirements : this.job_requirements}
                         )
                         .then(res => {
                             console.log(res)
                             alert('New task added 🫡')
                             this.job_title = ''
                             this.job_responsibilities = ''
                             this.job_requirements = ''

                             app.hideModal('jobdesc-creation')
                             app.getTasks()
                         })
                 },

                 async getTasks(){
                      let result = await axios({
                        url: 'http://localhost:5000/user',
                        method: 'get'
                      }).then(res => {
                        return res.data.username
                      })
                      this.username = result
                   username = this.username
                     axios({
                       url: 'http://localhost:5000/fetch/'+username,
                       method: 'get'
                     })
                     .then(res => {
                       this.emails = res.data.emails
                       this.jobdescs = res.data.jobdescs
                       this.lists = ['email', 'jobdesc']
                     })

                 },

                 deleteTask(id, type){
                     if (window.confirm('Are you sure you want to delete this task?')) {
                         axios.get("http://127.0.0.1:5000/delete_task/" + type + "/" + id + "/" + this.username)
                         .then(res => {
                             console.log(res)
                             alert('The task is gone 😮‍💨')
                             app.getTasks();
                         })
                     }
                 },

                 exportTask(id, type){
                     if (window.confirm('Export this task')) {
                         axios.get("http://127.0.0.1:5000/export_task/" + type + "/" + id)
                         .then(res => {
                             console.log(res)
                             alert('The task has been exported to a csv 😉')
                             app.getTasks();
                         })
                     }
                 },

             exportAll(){
                     axios.get("http://127.0.0.1:5000/export_all/" + this.username)
                     .then(res => {
                         console.log(res)
                         alert('The lists have been exported to a csv 😉')
                         app.getTasks();
                 })
             },

         },
             mounted: function(){
               this.getTasks()
             }
         })
