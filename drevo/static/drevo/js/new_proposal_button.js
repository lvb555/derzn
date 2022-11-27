$(document).ready(init)

function new_proposal_button() {
    let form = $(".add-new-answer")
    form.submit()
    form.val("")
    return true
}
